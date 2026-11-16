from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.contract import WALK_CEILING, night_cost, nightly_table, split_periods
from src.data import TARGET, arrival_date, read_raw

NUMERIC_FEATURES = [
    "lead_time",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "arrival_weekday",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "booking_changes",
    "days_in_waiting_list",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
]
CATEGORICAL_FEATURES = [
    "hotel",
    "arrival_date_month",
    "meal",
    "country",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
    "deposit_type",
    "customer_type",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
FORECAST_START = pd.Timestamp("2017-08-18")
FORECAST_END = pd.Timestamp("2017-08-31")
OUTPUT_PATH = Path(__file__).resolve().with_name(
    "oversell_2017-08-18_to_2017-08-31.csv"
)


def prepare_bookings(bookings: pd.DataFrame) -> pd.DataFrame:
    prepared = bookings.copy()
    prepared["arrival_date"] = arrival_date(prepared)
    prepared["arrival_weekday"] = prepared["arrival_date"].dt.dayofweek
    prepared["nights"] = (
        prepared["stays_in_weekend_nights"] + prepared["stays_in_week_nights"]
    )
    return prepared


def make_model() -> Pipeline:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=20)),
        ]
    )
    preprocess = ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocess),
            ("classifier", LogisticRegression(max_iter=500, solver="liblinear")),
        ]
    )


def model_oversell(nights: pd.DataFrame, safety_factor: float) -> np.ndarray:
    buffer = safety_factor * nights["spread"].to_numpy(dtype=float)
    return np.floor(
        np.maximum(nights["expected"].to_numpy(dtype=float) - buffer, 0.0)
    ).astype(int)


def choose_model_safety(
    nights: pd.DataFrame,
) -> tuple[float, dict[str, float | int | bool]]:
    expected = nights["expected"].to_numpy(dtype=float)
    spread = nights["spread"].to_numpy(dtype=float)
    positive_spread = spread > 0
    zero_oversell_factor = (
        float(np.max(expected[positive_spread] / spread[positive_spread]))
        if positive_spread.any()
        else 0.0
    )
    candidates = np.unique(
        np.concatenate(
            [
                np.arange(0.0, 12.01, 0.25),
                np.array([16.0, 24.0, 32.0, 64.0, zero_oversell_factor]),
            ]
        )
    )
    acceptable = []
    for factor in candidates:
        oversell = model_oversell(nights, float(factor))
        metrics = night_cost(nights, oversell)
        if metrics["walks_per_1000"] <= WALK_CEILING:
            acceptable.append((metrics["cost_eur"], metrics["walked_guests"], factor, metrics))
    if not acceptable:
        raise RuntimeError("No model safety setting meets the walk ceiling on choose data.")
    _, _, best_factor, best_metrics = min(acceptable, key=lambda row: (row[0], row[1], row[2]))
    return float(best_factor), best_metrics


def flat_oversell(
    nights: pd.DataFrame, hotel_rates: pd.Series, safety_margin: int
) -> np.ndarray:
    expected = nights["book"].astype(float) * nights.index.get_level_values("hotel").map(
        hotel_rates
    )
    return np.floor(np.maximum(expected.to_numpy() - safety_margin, 0.0)).astype(int)


def choose_flat_margin(
    nights: pd.DataFrame, hotel_rates: pd.Series
) -> tuple[int, dict[str, float | int | bool]]:
    hotel_rate = nights.index.get_level_values("hotel").map(hotel_rates)
    max_expected = float((nights["book"].to_numpy() * hotel_rate).max())
    candidates = range(int(np.ceil(max_expected)) + 2)
    acceptable = []
    for margin in candidates:
        metrics = night_cost(nights, flat_oversell(nights, hotel_rates, margin))
        if metrics["walks_per_1000"] <= WALK_CEILING:
            acceptable.append((metrics["cost_eur"], metrics["walked_guests"], margin, metrics))
    if not acceptable:
        raise RuntimeError("No flat-rule safety margin meets the walk ceiling on choose data.")
    _, _, best_margin, best_metrics = min(
        acceptable, key=lambda row: (row[0], row[1], row[2])
    )
    return int(best_margin), best_metrics


def print_metrics(
    label: str, metrics: dict[str, float | int | bool], arrivals: int
) -> None:
    print(
        f"{label}: cost EUR {metrics['cost_eur']:,.2f}; "
        f"empty rooms {metrics['empty_rooms']:,}; "
        f"walked guests {metrics['walked_guests']:,}; "
        f"walks/1,000 arrivals {metrics['walks_per_1000']:.2f}; "
        f"ceiling met {metrics['ceiling_met']}; "
        f"arrivals {arrivals:,}; nights {metrics['nights']:,}"
    )


def main() -> None:
    bookings = prepare_bookings(read_raw())
    train, choose, proof = split_periods(bookings)
    if train.empty or choose.empty or proof.empty:
        raise ValueError("The dataset must contain non-empty train, choose, and proof periods.")

    model = make_model()
    model.fit(train[FEATURES], train[TARGET])

    choose_prob = model.predict_proba(choose[FEATURES])[:, 1]
    choose_nights = nightly_table(choose, choose_prob)
    safety_factor, choose_model_metrics = choose_model_safety(choose_nights)

    train_rates = train.groupby("hotel")[TARGET].mean()
    choose_flat_nights = nightly_table(
        choose,
        choose["hotel"].map(train_rates).to_numpy(dtype=float),
    )
    flat_margin, choose_flat_metrics = choose_flat_margin(
        choose_flat_nights, train_rates
    )

    proof_prob = model.predict_proba(proof[FEATURES])[:, 1]
    proof_nights = nightly_table(proof, proof_prob)
    model_metrics = night_cost(
        proof_nights, model_oversell(proof_nights, safety_factor)
    )
    flat_metrics = night_cost(
        proof_nights, flat_oversell(proof_nights, train_rates, flat_margin)
    )
    arrivals = int((proof_nights["book"] - proof_nights["cancelled"]).sum())

    print("Proof period: 2017-01-01 through 2017-08-31")
    print(
        f"Selected model safety factor: {safety_factor:g} x nightly spread "
        f"(choose cost EUR {choose_model_metrics['cost_eur']:,.2f})"
    )
    print(f"Selected flat-rule safety margin: {flat_margin} rooms")
    print_metrics("Model", model_metrics, arrivals)
    print_metrics("Flat rule", flat_metrics, arrivals)
    print(
        f"Savings vs flat rule: EUR {flat_metrics['cost_eur'] - model_metrics['cost_eur']:,.2f}; "
        f"{flat_metrics['empty_rooms'] - model_metrics['empty_rooms']:,} fewer empty rooms"
    )

    forecast = proof[
        proof["arrival_date"].between(FORECAST_START, FORECAST_END)
    ]
    forecast_prob = model.predict_proba(forecast[FEATURES])[:, 1]
    forecast_nights = nightly_table(forecast, forecast_prob)
    hotels = sorted(bookings["hotel"].dropna().unique())
    all_nights = pd.MultiIndex.from_product(
        [hotels, pd.date_range(FORECAST_START, FORECAST_END, freq="D")],
        names=["hotel", "arrival_date"],
    )
    forecast_nights = forecast_nights.reindex(all_nights, fill_value=0)
    buffer = safety_factor * forecast_nights["spread"].to_numpy(dtype=float)
    forecast_output = forecast_nights.reset_index()[
        ["hotel", "arrival_date", "book", "expected"]
    ].rename(
        columns={
            "arrival_date": "arrival_date",
            "book": "bookings_on_book",
            "expected": "expected_cancellations",
        }
    )
    forecast_output["buffer"] = buffer
    forecast_output["oversell_rooms"] = model_oversell(forecast_nights, safety_factor)
    forecast_output["arrival_date"] = forecast_output["arrival_date"].dt.strftime("%Y-%m-%d")
    forecast_output["expected_cancellations"] = forecast_output[
        "expected_cancellations"
    ].round(2)
    forecast_output["buffer"] = forecast_output["buffer"].round(2)
    forecast_output.to_csv(OUTPUT_PATH, index=False)
    print(f"14-night oversell table written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

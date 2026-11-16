"""The production script executed every morning by the Revenue Manager.
Owned by: Build Lead

Loads the saved model and writes the 14-night oversell table.
Usage:
    python src/nightly.py --from 2017-08-18 --nights 14
"""
import argparse
import pathlib
import sys
import numpy as np
import pandas as pd
import joblib

import data
import contract
import features


def parse_args():
    parser = argparse.ArgumentParser(description="Nightly oversell recommendation engine.")
    parser.add_argument("--from", dest="from_date", type=str, default="2017-08-18",
                        help="Start arrival date (YYYY-MM-DD)")
    parser.add_argument("--nights", dest="nights", type=int, default=14,
                        help="Number of arrival nights to score")
    return parser.parse_args()


def generate_nightly_table(start_date="2017-08-18", n_nights=14):
    """Generates the 14-night oversell recommendation table for the Revenue Manager."""
    start_dt = pd.to_datetime(start_date)
    end_dt = start_dt + pd.Timedelta(days=n_nights)

    # 1. Locate and load model artifact
    candidate_paths = [
        pathlib.Path(__file__).resolve().parent.parent / "models" / "chosen_model.joblib",
        pathlib.Path("build2-starter/models/chosen_model.joblib"),
        pathlib.Path("models/chosen_model.joblib")
    ]
    model_path = next((p for p in candidate_paths if p.exists()), None)
    if not model_path:
        raise FileNotFoundError(
            "Model file not found! Please run 'python src/backtest.py' first to train and save the model."
        )

    saved_state = joblib.load(model_path)
    model = saved_state["model"]
    buffer_val = saved_state["buffer"]
    trained_cols = saved_state["columns"]

    # 2. Ingest and clean raw data
    raw = data.read_raw()
    raw["arrival_date"] = data.arrival_date(raw)
    clean = features.clean_bookings(raw)

    # 3. Filter to the requested arrival date window
    mask = (clean["arrival_date"] >= start_dt) & (clean["arrival_date"] < end_dt)
    window_bookings = clean[mask].copy()

    if len(window_bookings) == 0:
        print(f"Warning: No bookings found with arrival dates between {start_dt.date()} and {end_dt.date()}.")
        return pd.DataFrame()

    # 4. Extract Bin 1 features and predict probabilities
    X = features.extract_bin1_features(window_bookings).reindex(columns=trained_cols, fill_value=0)
    probs = model.predict_proba(X)[:, 1]

    # 5. Aggregate to nightly table using contract.py
    nights = contract.nightly_table(window_bookings, probs)

    # 6. Compute integer oversell count: k = max(floor(expected - buffer), 0)
    nights["buffer"] = buffer_val
    nights["oversell_k"] = np.maximum(np.floor(nights["expected"] - buffer_val), 0).astype(int)

    # 7. Format clean report table
    report = nights.reset_index()[["hotel", "arrival_date", "book", "expected", "buffer", "oversell_k"]]
    report["arrival_date"] = report["arrival_date"].dt.strftime("%Y-%m-%d")
    report["expected"] = report["expected"].round(1)

    # 8. Save output table to disk
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "data"
    out_path = out_dir / "nightly_output.csv"
    report.to_csv(out_path, index=False)
    return report


def main():
    args = parse_args()
    start_date = pd.to_datetime(args.from_date)
    end_date = start_date + pd.Timedelta(days=args.nights)

    print("=" * 70)
    print(" " * 18 + "RATEGAIN REVENUE SCIENCE SQUAD")
    print(" " * 15 + "DAILY OVERSALE RECOMMENDATION REPORT")
    print("=" * 70)
    print(f"Window Start: {start_date.date()} | Window End: {end_date.date()} ({args.nights} nights)\n")

    report = generate_nightly_table(start_date=args.from_date, n_nights=args.nights)
    if not report.empty:
        print(report.to_string(index=False))
        print("-" * 70)
        print(f"Report saved to: data/nightly_output.csv ({len(report)} rows)\n")


if __name__ == "__main__":
    main()

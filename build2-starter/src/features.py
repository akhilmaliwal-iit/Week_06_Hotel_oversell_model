from random import Random
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

bin1_features = [
    'hotel',
    'lead_time',
    'adults',
    'children',
    'babies',
    'country',
    'market_segment',
    'distribution_channel',
    'is_repeated_guest',
    'previous_cancellations',
    'previous_bookings_not_canceled',
    'deposit_type',
    'agent',
    'company',
    'customer_type',
    'adr',
]

bin2_features = [
    'arrival_date_year',
    'arrival_date_month',
    'arrival_date_week_number',
    'arrival_date_day_of_month',
    'stays_in_weekend_nights',
    'stays_in_week_nights',
    'meal',
    'reserved_room_type',
    'booking_changes',
    'days_in_waiting_list',
    'required_car_parking_spaces',
    'total_of_special_requests',
]

bin3_features = [
    'assigned_room_type',
    'reservation_status',
    'reservation_status_date',
]

run_b_features = bin1_features + bin2_features+bin3_features


def load_data():
    data_path = Path(__file__).resolve().parent.parent / 'data' / 'hotels.csv'
    df = pd.read_csv(data_path)
    df['arrival_date'] = pd.to_datetime(
        df['arrival_date_year'].astype(str)
        + '-'
        + df['arrival_date_month']
        + '-'
        + df['arrival_date_day_of_month'].astype(str),
        format='%Y-%B-%d',
    )
    return df

def clean_bookings(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the raw hotel bookings dataframe based on documented decisions.
    
    1. Drops 180 ghost bookings where adults + children + babies == 0.
    2. Drops 1 billing error row where adr < 0.
    3. Imputes missing children with 0 (4 rows).
    4. Imputes missing country with 'Unknown' (488 rows).
    5. Imputes missing agent (16,340) and company (112,593) with 0 (direct booking).
    6. Creates 'nights' column as stays_in_weekend_nights + stays_in_week_nights.
    """
    data = df.copy()

    # 1. Drop ghost bookings (180 rows)
    has_guests = (data["adults"] + data["children"].fillna(0) + data["babies"]) > 0
    data = data[has_guests]

    # 2. Drop negative ADR (1 row)
    data = data[data["adr"] >= 0]

    # 3. Impute missing children with 0
    data["children"] = data["children"].fillna(0).astype(int)

    # 4. Impute missing country with 'Unknown'
    data["country"] = data["country"].fillna("Unknown")

    # 5. Impute agent and company with 0
    data["agent"] = data["agent"].fillna(0).astype(int)
    data["company"] = data["company"].fillna(0).astype(int)

    # 6. Total length of stay (nights)
    data["nights"] = data["stays_in_weekend_nights"] + data["stays_in_week_nights"]

    return data


def random_time_split(df: pd.DataFrame, random_state: int = 42):
    """Split rows at seeded, randomized date boundaries without mixing time periods."""
    if "arrival_date" not in df.columns:
        raise ValueError("df must contain an arrival_date column")
    if df["arrival_date"].isna().any():
        raise ValueError("arrival_date cannot contain missing values")

    dates = pd.Index(df["arrival_date"].unique()).sort_values()
    if len(dates) < 3:
        raise ValueError("at least three unique arrival dates are required")

    jitter = max(1, int(len(dates) * 0.05))
    rng = Random(random_state)
    train_cut = rng.randint(
        max(1, int(len(dates) * 0.70) - jitter),
        min(len(dates) - 2, int(len(dates) * 0.70) + jitter),
    )
    validation_cut = rng.randint(
        max(train_cut + 1, int(len(dates) * 0.85) - jitter),
        min(len(dates) - 1, int(len(dates) * 0.85) + jitter),
    )

    train_end = dates[train_cut]
    validation_end = dates[validation_cut]
    train_df = df[df["arrival_date"] < train_end]
    validation_df = df[
        (df["arrival_date"] >= train_end)
        & (df["arrival_date"] < validation_end)
    ]
    test_df = df[df["arrival_date"] >= validation_end]
    return train_df, validation_df, test_df


def evaluate_logistic_regression(model, eval_df, features, run_name):
    X_eval = eval_df[features]
    y_eval = eval_df["is_canceled"]
    predictions = model.predict_proba(X_eval)[:, 1]
    auc = roc_auc_score(y_eval, predictions)

    print(f"{run_name} ROC-AUC:", round(auc, 4))
    return auc


def run_logistic_regression(train_df, val_df, features, run_name):
    X_train = train_df[features]
    y_train = train_df['is_canceled']

    categorical_cols = X_train.select_dtypes(
    include=['object', 'category', 'str']).columns.tolist()
    for col in ['agent', 'company']:
        if col in features and col not in categorical_cols:
            categorical_cols.append(col)

    numerical_cols = [col for col in features if col not in categorical_cols]

    numerical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore')),
    ])

    preprocessor = ColumnTransformer([
        ('num', numerical_pipeline, numerical_cols),
        ('cat', categorical_pipeline, categorical_cols),
    ])

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(max_iter=2000)),
    ])

    model.fit(X_train, y_train)
    auc = evaluate_logistic_regression(model, val_df, features, run_name)
    return model, auc


if __name__ == '__main__':
    df = load_data()
    print(df.shape)
    data = clean_bookings(df)
    print(data.shape)
    train_df = data[data['arrival_date'] < '2016-07-01']
    choose_df = data[(data['arrival_date'] >= '2016-07-01') & (data['arrival_date'] < '2017-01-01')]
    proof_df = data[data['arrival_date'] >= '2017-01-01']

    model_A, auc_A = run_logistic_regression(
        train_df,
        choose_df,
        bin1_features,
        'Run A - Bin 1 Validation',
    )
    evaluate_logistic_regression(model_A, proof_df, bin1_features, 'Run A - Bin 1 Proof Test')

    model_B, auc_B = run_logistic_regression(
        train_df,
        choose_df,
        run_b_features,
        'Run B - All Honest Validation',
    )
    evaluate_logistic_regression(model_B, proof_df, run_b_features, 'Run B - All Honest Proof Test')

    development_data = data[data['arrival_date'] < '2017-01-01']
    random_train_df, random_choose_df, random_test_df = random_time_split(development_data)
    random_model, random_auc = run_logistic_regression(
        random_train_df,
        random_choose_df,
        bin1_features,
        'Random Time Split - Validation',
    )
    evaluate_logistic_regression(
        random_model,
        random_test_df,
        bin1_features,
        'Random Time Split - Test',
    )

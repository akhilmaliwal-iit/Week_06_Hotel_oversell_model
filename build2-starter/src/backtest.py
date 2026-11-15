"""
src/backtest.py  -  Model Lead script (final)

Flow:
  1. Chronological split via contract.split_periods (Train / Choose / Proof)
  2. Six methods: Zero, Client Flat Rule, Lookup Table, Logistic Regression,
     HistGradientBoosting, and LightGBM with early stopping
  3. Per method: sweep buffers 0..30 on CHOOSE, keep the cheapest one under the walk ceiling
  4. Score PROOF exactly once per method with the frozen buffer
  5. Print the Grand Method Table (Slide 5) and save it to evidence/method_table.csv
  6. Save the Choose buffer-sweep curve (Slide 6) to evidence/slide06_buffer_curve.png
  7. Save the winner (picked on Choose cost) to models/chosen_model.joblib

Assumes (edit score() if your contract differs):
  - contract.night_cost(nights, oversell=k) -> dict: cost_eur, empty_rooms, walked_guests,
    walks_per_1000, ceiling_met
  - contract.nightly_table(df, prob) -> DataFrame with 'expected' and 'spread'
Run from the project root:  python src/final_backtest.py
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier, early_stopping
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import contract
import data
import features

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
TARGET = "is_canceled"
CANDIDATE_BUFFERS = range(0, 31)   # must reach 16 for the Flat Rule (range(0, 10) returns None)
TOP_N = 10                         # keep top-N values for high-cardinality columns
CEILING = contract.WALK_CEILING
EVIDENCE_DIR = Path("evidence")
MODEL_PATH = Path("models/chosen_model.joblib")

MODEL_FEATURES = features.bin1_features
CAT_COLS = features.bin1_categorical_cols
HIGH_CARD = ["country", "agent", "company"]
# Bin 2 and Bin 3 features are excluded from the honest booking-time model.


# ----------------------------------------------------------------------------
# Scoring helpers
# ----------------------------------------------------------------------------
def score(nights, k):
    """Only place that talks to contract.night_cost."""
    r = contract.night_cost(nights, oversell=k)
    return {
        "cost": r["cost_eur"],
        "empty": r["empty_rooms"],
        "walks": r["walked_guests"],
        "walk_rate": r["walks_per_1000"],
        "ok": r["ceiling_met"],
    }


def k_from_buffer(nights, b):
    """k = max(floor(mu - b), 0): whole number, never negative."""
    return np.maximum(np.floor(nights["expected"] - b), 0).astype(int)


def k_from_uncertainty(nights, z):
    """k = max(floor(mu - z*spread), 0): buffer scales with that night's spread."""
    return np.maximum(np.floor(nights["expected"] - z * nights["spread"]), 0).astype(int)


def sweep_buffers(choose_nights):
    """Score every candidate buffer on CHOOSE. Returns a DataFrame (one row per buffer)."""
    rows = []
    for b in CANDIDATE_BUFFERS:
        s = score(choose_nights, k_from_buffer(choose_nights, b))
        rows.append({"buffer": b, "cost": s["cost"], "walk_rate": s["walk_rate"], "ok": s["ok"]})
    return pd.DataFrame(rows)


def best_buffer(sweep):
    """Cheapest buffer that meets the ceiling. Proof is never touched here."""
    ok = sweep[sweep["ok"]]
    if ok.empty:
        raise RuntimeError("No buffer met the walk ceiling - widen CANDIDATE_BUFFERS")
    return int(ok.loc[ok["cost"].idxmin(), "buffer"])


# ----------------------------------------------------------------------------
# Feature preparation (everything learned from TRAIN only)
# ----------------------------------------------------------------------------
def learn_top_categories(train):
    return {c: train[c].fillna("unknown").astype(str).value_counts().head(TOP_N).index.tolist()
            for c in HIGH_CARD}


def prep(df, top_cats):
    """Select Bin 1 columns, clean missing values, collapse rare categories to 'other'."""
    X = df[MODEL_FEATURES].copy()
    X["children"] = X["children"].fillna(0)
    for c in CAT_COLS:
        X[c] = X[c].fillna("unknown").astype(str)
    for c in HIGH_CARD:
        X[c] = X[c].where(X[c].isin(top_cats[c]), "other")
    return X


def make_X(df, top_cats, columns=None):
    """One-hot encode; for Choose/Proof align to Train's columns (no unseen/missing dummies)."""
    X = pd.get_dummies(prep(df, top_cats), columns=CAT_COLS, dtype=float)
    return X if columns is None else X.reindex(columns=columns, fill_value=0)


# ----------------------------------------------------------------------------
# Probability methods -> (p_choose, p_proof) per booking
# ----------------------------------------------------------------------------
def flat_probs(train, choose, proof):
    rate = train.groupby("hotel")[TARGET].mean()           # City ~0.417, Resort ~0.278
    return choose["hotel"].map(rate).values, proof["hotel"].map(rate).values


def lookup_probs(train, choose, proof):
    bins = [-1, 7, 30, 100, 10_000]                        # fixed bins: no NaN on unseen lead times
    labels = ["short", "mid", "long", "very_long"]
    keys = ["hotel", "market_segment", "lead_band"]

    def band(df):
        d = df[["hotel", "market_segment", "lead_time"]].copy()
        d["lead_band"] = pd.cut(d["lead_time"], bins=bins, labels=labels).astype(str)
        return d

    tr = band(train)
    tr[TARGET] = train[TARGET].values
    table = tr.groupby(keys)[TARGET].mean()
    hotel_rate = train.groupby("hotel")[TARGET].mean()     # fallback for unseen combinations

    def lookup(df):
        d = band(df)
        p = d.join(table.rename("p"), on=keys)["p"]
        return p.fillna(df["hotel"].map(hotel_rate)).values

    return lookup(choose), lookup(proof)


def model_probs(model, X_train, y_train, X_choose, X_proof):
    model.fit(X_train, y_train)
    return model.predict_proba(X_choose)[:, 1], model.predict_proba(X_proof)[:, 1]   # not predict()


def early_stopping_model_probs(model, X_train, y_train, X_choose, y_choose, X_proof):
    model.fit(
        X_train,
        y_train,
        eval_X=X_choose,
        eval_y=y_choose,
        callbacks=[early_stopping(50, verbose=False)],
    )
    return model.predict_proba(X_choose)[:, 1], model.predict_proba(X_proof)[:, 1]


# ----------------------------------------------------------------------------
# Evidence outputs
# ----------------------------------------------------------------------------
def save_buffer_curve(sweep, chosen_b, title):
    """Slide 6: cost curve (left axis), walks/1k (right axis), ceiling line, chosen buffer."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping buffer curve (pip install matplotlib)")
        return
    EVIDENCE_DIR.mkdir(exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(sweep["buffer"], sweep["cost"] / 1e6, color="tab:blue", marker="o", ms=3)
    ax1.set_xlabel("Safety buffer b (rooms)")
    ax1.set_ylabel("Cost on Choose (EUR millions)", color="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(sweep["buffer"], sweep["walk_rate"], color="tab:red", marker="s", ms=3)
    ax2.axhline(CEILING, color="black", ls="--", lw=1)
    ax2.text(sweep["buffer"].max(), CEILING, " ceiling 10/1k", va="bottom", ha="right")
    ax2.set_ylabel("Walks per 1,000 arrivals", color="tab:red")
    ax1.axvline(chosen_b, color="green", ls=":", lw=1.5)
    ax1.set_title(f"{title}: buffer selection on Choose (chosen b={chosen_b})")
    fig.tight_layout()
    fig.savefig(EVIDENCE_DIR / "slide06_buffer_curve.png", dpi=150)
    plt.close(fig)
    print(f"Saved {EVIDENCE_DIR / 'slide06_buffer_curve.png'}")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    raw = data.read_raw()
    raw["arrival_date"] = data.arrival_date(raw)
    clean = features.clean_bookings(raw)
    train, choose, proof = contract.split_periods(clean)   # chronological, never shuffle
    print(f"Rows  train={len(train):,}  choose={len(choose):,}  proof={len(proof):,}")

    top_cats = learn_top_categories(train)
    X_train = make_X(train, top_cats)
    cols = X_train.columns.tolist()
    X_choose, X_proof = make_X(choose, top_cats, cols), make_X(proof, top_cats, cols)
    y_train = train[TARGET]

    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))
    hgb = HistGradientBoostingClassifier(random_state=42)
    lgbm = LGBMClassifier(
        n_estimators=2000,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        verbosity=-1,
    )

    methods = {
        "Client Flat Rule":     (flat_probs(train, choose, proof), None),
        "Lookup Table":         (lookup_probs(train, choose, proof), None),
        "Logistic Regression":  (model_probs(lr, X_train, y_train, X_choose, X_proof), lr),
        "HistGradientBoosting": (model_probs(hgb, X_train, y_train, X_choose, X_proof), hgb),
        "LightGBM":             (early_stopping_model_probs(
            lgbm, X_train, y_train, X_choose, choose[TARGET], X_proof,
        ), lgbm),
    }
    print(f"LightGBM best iteration: {lgbm.best_iteration_}")

    rows, choose_costs, sweeps = [], {}, {}

    # Baseline 0: sell no extra rooms
    n0 = contract.nightly_table(proof, np.zeros(len(proof)))
    rows.append(("Zero Oversell", None, 0, score(n0, np.zeros(len(n0), dtype=int))))

    for name, ((p_choose, p_proof), _) in methods.items():
        n_choose = contract.nightly_table(choose, p_choose)
        n_proof = contract.nightly_table(proof, p_proof)

        sweeps[name] = sweep_buffers(n_choose)                               # Choose only
        b = best_buffer(sweeps[name])
        choose_costs[name] = float(sweeps[name].loc[sweeps[name]["buffer"] == b, "cost"].iloc[0])

        s = score(n_proof, k_from_buffer(n_proof, b))                        # Proof, once
        auc = None if name == "Client Flat Rule" else roc_auc_score(proof[TARGET], p_proof)
        rows.append((name, auc, b, s))

    flat_cost = next(r[3]["cost"] for r in rows if r[0] == "Client Flat Rule")

    # Grand Method Table (Slide 5): rank by euro savings, not AUC
    print(f"\n{'Method':<22}{'AUC':>8}{'Buffer':>8}{'Empty':>9}{'Walks':>7}"
          f"{'Walks/1k':>10}{'Cost (EUR)':>16}{'Savings vs Flat':>18}")
    table = []
    for name, auc, b, s in rows:
        auc_txt = f"{auc:.4f}" if auc is not None else "-"
        savings = flat_cost - s["cost"]
        print(f"{name:<22}{auc_txt:>8}{b:>8}{s['empty']:>9,.0f}{s['walks']:>7,.0f}"
              f"{s['walk_rate']:>10.2f}{s['cost']:>16,.2f}{savings:>18,.2f}")
        table.append({"method": name, "auc": auc, "choose_buffer": b, "empty_rooms": s["empty"],
                      "walks": s["walks"], "walks_per_1k": s["walk_rate"],
                      "total_cost_eur": s["cost"], "savings_vs_flat_eur": savings})
    EVIDENCE_DIR.mkdir(exist_ok=True)
    pd.DataFrame(table).to_csv(EVIDENCE_DIR / "method_table.csv", index=False)

    # Winner: lowest CHOOSE cost among ML models (never decided on Proof)
    ml = {
        k: v
        for k, v in choose_costs.items()
        if k in ("Logistic Regression", "HistGradientBoosting", "LightGBM")
    }
    winner = min(ml, key=ml.get)
    w_buffer = next(r[2] for r in rows if r[0] == winner)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"model": methods[winner][1], "buffer": w_buffer,
                 "columns": cols, "top_categories": top_cats},    # nightly.py needs all four
                MODEL_PATH)
    print(f"\nSaved {MODEL_PATH} -> {winner}, buffer={w_buffer}")

    # Slide 6: buffer sweep for the winner
    save_buffer_curve(sweeps[winner], w_buffer, winner)

    # Day 3: fixed buffer vs uncertainty buffer, on CHOOSE only
    cn = contract.nightly_table(choose, methods[winner][0][0])
    if "spread" in cn.columns:
        print("\nUncertainty buffer on Choose:")
        for z in (1.0, 1.28, 1.64):
            s = score(cn, k_from_uncertainty(cn, z))
            print(f"  z={z:<5} cost={s['cost']:>14,.2f}  walks/1k={s['walk_rate']:.2f}  ok={s['ok']}")


if __name__ == "__main__":
    main()
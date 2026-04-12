import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report

FEATURE_COLS = [
    "sentiment_positive", "sentiment_negative", "sentiment_neutral",
    "sentiment_score", "rsi", "macd", "bb_upper", "bb_lower",
    "atr", "bb_width", "rsi_overbought", "rsi_oversold"
]

LABEL_COL = "signal"


def train(df: pd.DataFrame, model_path: str = "model/lgbm_model.pkl") -> None:
    """
    Train LightGBM on historical labeled feature vectors.
    Saves trained model to disk.
    """

    # Split into features and labels — no train_test_split needed
    # TimeSeriesSplit handles the splitting inside the loop
    X = df[FEATURE_COLS]
    y = df[LABEL_COL]

    tscv = TimeSeriesSplit(n_splits=5)

    # Cross-validation loop — train on past, test on future each fold
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05)  # ✅ fixed typo
        model.fit(X_train, y_train)
        preds = model.predict(X_val)

        print(f"\n--- Fold {fold + 1} ---")          # shows which fold we're on
        print(classification_report(y_val, preds))   # precision, recall, F1

    # Final model trained on ALL data — best version for production
    print("\nTraining final model on full dataset...")
    final_model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05)  # ✅ fixed
    final_model.fit(X, y)

    # Save to disk — like serializing in C#
    joblib.dump(final_model, model_path)
    print(f"Model saved to {model_path}")  # ✅ more descriptive message
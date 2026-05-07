import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
from pathlib import Path

FEATURE_COLS = [
    "sentiment_positive", "sentiment_negative", "sentiment_neutral",
    "sentiment_score", "rsi", "macd", "bb_upper", "bb_lower",
    "atr", "bb_width", "rsi_overbought", "rsi_oversold"
]

LABEL_COL = "signal"


def train(df: pd.DataFrame, model_path: str = "model/lgbm_model.pkl") -> None:
    try:
        if df.empty:
            print("[trainer] Error: Empty training dataframe")
            return None

        required_columns = FEATURE_COLS + [LABEL_COL]
        missing_columns = [column for column in required_columns if column not in df.columns]
        if missing_columns:
            print(f"[trainer] Error: Missing columns {missing_columns}")
            return None

        X = df[FEATURE_COLS]
        y = df[LABEL_COL]
        split_count = min(3, len(X) - 1) if len(X) < 20 else min(5, len(X) - 1)
        if split_count >= 2:
            tscv = TimeSeriesSplit(n_splits=split_count)
            for fold, (train_idx, val_idx) in enumerate(tscv.split(X), start=1):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                model = lgb.LGBMClassifier(
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=42,
                    min_data_in_leaf=1,
                    min_data_in_bin=1,
                    num_leaves=8,
                    verbosity=-1
                )
                model.fit(X_train, y_train)
                preds = model.predict(X_val)
                print(f"\n--- Fold {fold} ---")
                print(classification_report(y_val, preds, zero_division=0))

        print("\nTraining final model on full dataset...")
        final_model = lgb.LGBMClassifier(
            n_estimators=100,
            learning_rate=0.05,
            random_state=42,
            min_data_in_leaf=1,
            min_data_in_bin=1,
            num_leaves=8,
            verbosity=-1
        )
        final_model.fit(X, y)

        model_path_obj = Path(model_path)
        model_path_obj.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(final_model, model_path_obj)
        print(f"Model saved to {model_path_obj}")
        return None
    except Exception as e:
        print(f"[trainer] Error: {e}")
        return None

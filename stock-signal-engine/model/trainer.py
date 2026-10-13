import logging
from pathlib import Path
from typing import Optional

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "sentiment_positive", "sentiment_negative", "sentiment_neutral",
    "sentiment_score", "rsi", "macd", "bb_upper", "bb_lower",
    "atr", "bb_width", "rsi_overbought", "rsi_oversold"
]

LABEL_COL = "signal"


def train(
    df: pd.DataFrame,
    model_path: str = "model/lgbm_model.pkl",
    n_splits: int = 5,
) -> Optional[dict]:
    """
    Trains a LightGBM classifier with Walk-Forward (TimeSeriesSplit) cross-validation,
    evaluates classification and ROC-AUC metrics, displays feature importances,
    and saves the production model with macOS-safe n_jobs=1.
    """
    try:
        if df.empty:
            print("[trainer] Error: Empty training dataframe")
            return None

        required_columns = FEATURE_COLS + [LABEL_COL]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"[trainer] Error: Missing columns {missing_columns}")
            return None

        # Clean NaNs and infinite values
        clean_df = df[required_columns].copy()
        clean_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        clean_df.dropna(inplace=True)

        X = clean_df[FEATURE_COLS]
        y = clean_df[LABEL_COL].astype(int)

        print(f"\n[trainer] Training on {len(X):,} samples ({FEATURE_COLS})")
        print(f"[trainer] Target distribution: Class 0: {(y == 0).sum():,} ({(y == 0).mean()*100:.1f}%) | "
              f"Class 1: {(y == 1).sum():,} ({(y == 1).mean()*100:.1f}%)")

        # Walk-Forward Cross-Validation
        split_count = min(n_splits, max(2, len(X) // 100))
        tscv = TimeSeriesSplit(n_splits=split_count)
        oof_preds = []
        oof_targets = []
        oof_probs = []

        print(f"\n--- {split_count}-Fold Walk-Forward TimeSeriesSplit Validation ---")
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X), start=1):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            fold_model = lgb.LGBMClassifier(
                n_estimators=150,
                learning_rate=0.03,
                num_leaves=15,
                min_child_samples=25,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42 + fold,
                n_jobs=1,
                verbosity=-1,
            )
            fold_model.fit(X_train, y_train)
            probs = fold_model.predict_proba(X_val)[:, 1]
            preds = (probs >= 0.50).astype(int)

            try:
                fold_auc = roc_auc_score(y_val, probs)
            except Exception:
                fold_auc = 0.50

            print(f"Fold {fold}/{split_count} (Train: {len(X_train):,}, Val: {len(X_val):,}): "
                  f"ROC-AUC: {fold_auc:.4f} | Accuracy: {(preds == y_val).mean()*100:.1f}%")

            oof_preds.extend(preds)
            oof_targets.extend(y_val)
            oof_probs.extend(probs)

        if oof_targets:
            total_auc = roc_auc_score(oof_targets, oof_probs)
            print(f"\n[trainer] Aggregate Out-Of-Fold ROC-AUC: {total_auc:.4f}")
            print(classification_report(oof_targets, oof_preds, target_names=["HOLD/SKIP (0)", "BUY (1)"], zero_division=0))

        # Final Production Model Training
        print("Training final production model on full dataset...")
        final_model = lgb.LGBMClassifier(
            n_estimators=150,
            learning_rate=0.03,
            num_leaves=15,
            min_child_samples=25,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=1,
            verbosity=-1,
        )
        final_model.fit(X, y)
        final_model.set_params(n_jobs=1)

        # Feature Importance Analysis
        importances = final_model.feature_importances_
        fi_df = pd.DataFrame({
            "Feature": FEATURE_COLS,
            "Importance": importances,
        }).sort_values(by="Importance", ascending=False)

        print("\n=== Model Feature Importance (Split Count) ===")
        for _, row in fi_df.iterrows():
            bar = "█" * int(row["Importance"] / max(importances.max(), 1) * 25)
            print(f"  {row['Feature']:<20} {int(row['Importance']):>5}  {bar}")

        # Persist to disk
        model_path_obj = Path(model_path)
        model_path_obj.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(final_model, model_path_obj)
        print(f"\n[trainer] Production model successfully saved to {model_path_obj}")

        return {
            "samples": len(X),
            "oof_auc": total_auc if oof_targets else 0.5,
            "feature_importances": fi_df.to_dict(orient="records"),
        }

    except Exception as e:
        print(f"[trainer] Error during training: {e}")
        return None

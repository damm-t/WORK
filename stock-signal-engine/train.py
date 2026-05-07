from pathlib import Path

import pandas as pd

from model.trainer import FEATURE_COLS, LABEL_COL, train


def load_training_dataframe() -> pd.DataFrame:
    try:
        candidate_paths = [
            Path("data/training_features.csv"),
            Path("data/training_features.parquet"),
            Path("training_features.csv"),
            Path("training_features.parquet"),
        ]

        for candidate_path in candidate_paths:
            if not candidate_path.exists():
                continue

            if candidate_path.suffix == ".csv":
                return pd.read_csv(candidate_path)

            if candidate_path.suffix == ".parquet":
                return pd.read_parquet(candidate_path)

        return build_bootstrap_dataframe()
    except Exception as e:
        print(f"[train.py] Error: {e}")
        return pd.DataFrame()


def build_bootstrap_dataframe() -> pd.DataFrame:
    try:
        records = [
            {"sentiment_positive": 1, "sentiment_negative": 0, "sentiment_neutral": 0, "sentiment_score": 0.91, "rsi": 28.0, "macd": 1.45, "bb_upper": 201.0, "bb_lower": 187.0, "atr": 4.2, "bb_width": 14.0, "rsi_overbought": 0, "rsi_oversold": 1, "signal": 1},
            {"sentiment_positive": 0, "sentiment_negative": 1, "sentiment_neutral": 0, "sentiment_score": 0.82, "rsi": 74.0, "macd": -1.05, "bb_upper": 322.0, "bb_lower": 297.0, "atr": 6.5, "bb_width": 25.0, "rsi_overbought": 1, "rsi_oversold": 0, "signal": 0},
            {"sentiment_positive": 1, "sentiment_negative": 0, "sentiment_neutral": 0, "sentiment_score": 0.88, "rsi": 35.0, "macd": 1.18, "bb_upper": 154.0, "bb_lower": 144.0, "atr": 3.1, "bb_width": 10.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 1},
            {"sentiment_positive": 0, "sentiment_negative": 0, "sentiment_neutral": 1, "sentiment_score": 0.51, "rsi": 48.0, "macd": 0.12, "bb_upper": 111.0, "bb_lower": 105.0, "atr": 2.0, "bb_width": 6.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 0},
            {"sentiment_positive": 1, "sentiment_negative": 0, "sentiment_neutral": 0, "sentiment_score": 0.79, "rsi": 32.0, "macd": 0.94, "bb_upper": 266.0, "bb_lower": 251.0, "atr": 5.7, "bb_width": 15.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 1},
            {"sentiment_positive": 0, "sentiment_negative": 1, "sentiment_neutral": 0, "sentiment_score": 0.87, "rsi": 69.0, "macd": -0.84, "bb_upper": 141.0, "bb_lower": 129.0, "atr": 3.4, "bb_width": 12.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 0},
            {"sentiment_positive": 0, "sentiment_negative": 0, "sentiment_neutral": 1, "sentiment_score": 0.49, "rsi": 44.0, "macd": -0.08, "bb_upper": 91.0, "bb_lower": 84.0, "atr": 1.7, "bb_width": 7.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 0},
            {"sentiment_positive": 1, "sentiment_negative": 0, "sentiment_neutral": 0, "sentiment_score": 0.93, "rsi": 26.0, "macd": 1.67, "bb_upper": 415.0, "bb_lower": 389.0, "atr": 7.3, "bb_width": 26.0, "rsi_overbought": 0, "rsi_oversold": 1, "signal": 1},
            {"sentiment_positive": 0, "sentiment_negative": 1, "sentiment_neutral": 0, "sentiment_score": 0.76, "rsi": 71.0, "macd": -0.93, "bb_upper": 178.0, "bb_lower": 163.0, "atr": 3.8, "bb_width": 15.0, "rsi_overbought": 1, "rsi_oversold": 0, "signal": 0},
            {"sentiment_positive": 1, "sentiment_negative": 0, "sentiment_neutral": 0, "sentiment_score": 0.72, "rsi": 38.0, "macd": 0.63, "bb_upper": 133.0, "bb_lower": 125.0, "atr": 2.6, "bb_width": 8.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 1},
            {"sentiment_positive": 0, "sentiment_negative": 0, "sentiment_neutral": 1, "sentiment_score": 0.53, "rsi": 50.0, "macd": 0.03, "bb_upper": 246.0, "bb_lower": 235.0, "atr": 4.1, "bb_width": 11.0, "rsi_overbought": 0, "rsi_oversold": 0, "signal": 0},
            {"sentiment_positive": 0, "sentiment_negative": 1, "sentiment_neutral": 0, "sentiment_score": 0.81, "rsi": 77.0, "macd": -1.26, "bb_upper": 302.0, "bb_lower": 280.0, "atr": 6.1, "bb_width": 22.0, "rsi_overbought": 1, "rsi_oversold": 0, "signal": 0},
        ]
        training_df = pd.DataFrame(records)
        ordered_columns = FEATURE_COLS + [LABEL_COL]
        return training_df[ordered_columns]
    except Exception as e:
        print(f"[train.py] Error: {e}")
        return pd.DataFrame()


def main() -> None:
    try:
        training_df = load_training_dataframe()
        if training_df.empty:
            print("[train.py] Error: Empty training dataframe")
            return None

        train(training_df)
        return None
    except Exception as e:
        print(f"[train.py] Error: {e}")
        return None


if __name__ == "__main__":
    main()

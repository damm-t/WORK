"""
Early-Signal Stock Scanner — research only. Reads a CSV, scores four signals
out of 100, ranks candidates, writes watchlist.csv. No trading, no broker, no live data.
Standard library only. EXAMPLE DATA in sample_data.csv is fictional.
"""
import csv
import datetime
import sys

# Educational defaults
WEIGHTS = {"volume": 30, "momentum": 25, "news": 25, "attention": 20}
THRESHOLD = 50  # minimum score to appear on the watchlist
TOP_N = 5


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def score_row(r):
    # 1. Volume: 1x -> 0, 3x+ -> full (30 pts)
    vol_ratio = float(r["volume_today"]) / max(float(r["volume_avg_20d"]), 1)
    volume = clamp((vol_ratio - 1) / 2)

    # 2. Momentum: 0% -> 0, +10%+ -> full (25 pts)
    momentum = clamp(float(r["price_change_5d_pct"]) / 10)

    # 3. News: 0 items -> 0, 5+ items -> full (25 pts)
    news = clamp(float(r["news_items_7d"]) / 5)

    # 4. Attention: 1x -> 0, 3x+ -> full (20 pts)
    att_ratio = float(r["mentions_7d"]) / max(float(r["mentions_avg_7d"]), 1)
    attention = clamp((att_ratio - 1) / 2)

    parts = {
        "volume": round(volume * WEIGHTS["volume"], 1),
        "momentum": round(momentum * WEIGHTS["momentum"], 1),
        "news": round(news * WEIGHTS["news"], 1),
        "attention": round(attention * WEIGHTS["attention"], 1),
    }
    parts["total"] = round(sum(parts.values()), 1)
    return parts


def main(path="sample_data.csv"):
    required = [
        "candidate",
        "volume_today",
        "volume_avg_20d",
        "price_change_5d_pct",
        "news_items_7d",
        "mentions_7d",
        "mentions_avg_7d",
    ]

    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        sys.exit("No data rows found in " + path)

    missing = [c for c in required if c not in rows[0]]
    if missing:
        sys.exit("CSV is missing columns: " + ", ".join(missing))

    scored = []
    for r in rows:
        s = score_row(r)
        s["candidate"] = r["candidate"]
        scored.append(s)

    scored.sort(key=lambda s: s["total"], reverse=True)
    watch = [s for s in scored if s["total"] >= THRESHOLD][:TOP_N]

    today = datetime.date.today().isoformat()
    with open("watchlist.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "rank", "candidate", "total", "volume", "momentum", "news", "attention", "status"])
        for i, s in enumerate(watch, 1):
            w.writerow([
                today,
                i,
                s["candidate"],
                s["total"],
                s["volume"],
                s["momentum"],
                s["news"],
                s["attention"],
                "REVIEW REQUIRED",
            ])

    print(f"Scored {len(scored)} candidates. {len(watch)} passed threshold {THRESHOLD}.")
    print(f"{'RANK':<5}{'CANDIDATE':<14}{'TOTAL':>7}{'VOL':>6}{'MOM':>6}{'NEWS':>6}{'ATT':>6}")
    for i, s in enumerate(scored, 1):
        flag = " <- watchlist" if s in watch else ""
        print(f"{i:<5}{s['candidate']:<14}{s['total']:>7}{s['volume']:>6}{s['momentum']:>6}{s['news']:>6}{s['attention']:>6}{flag}")

    print("\nResearch only. Review every candidate at the original source. Nothing is traded.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv")

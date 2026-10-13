"""
Stock Universe Definitions
==========================
core : 28 mega-caps across all 11 GICS sectors (fast scans, daily use)
wide : ~90 large-caps across all 11 GICS sectors (deeper selection pools)

Sector ETFs (SECTOR_ETF) power the sector-trend filter in the scanner.
"""

CORE_UNIVERSE = {
    "Technology":      ["NVDA", "AAPL", "MSFT", "AMD"],
    "Communication":   ["GOOGL", "META", "NFLX"],
    "Consumer Disc.":  ["AMZN", "TSLA", "HD"],
    "Financials":      ["JPM", "V", "GS"],
    "Healthcare":      ["JNJ", "UNH", "LLY"],
    "Energy":          ["XOM", "CVX"],
    "Industrials":     ["CAT", "BA"],
    "Staples":         ["PG", "KO"],
    "Utilities":       ["NEE", "DUK"],
    "Materials":       ["LIN", "FCX"],
    "Real Estate":     ["PLD", "AMT"],
}

WIDE_UNIVERSE = {
    "Technology":      ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "ADBE",
                        "CSCO", "QCOM", "TXN", "IBM", "INTC", "NOW", "AMD"],
    "Communication":   ["GOOGL", "META", "NFLX", "DIS", "TMUS", "CMCSA", "VZ", "T"],
    "Consumer Disc.":  ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX",
                        "BKNG"],
    "Financials":      ["JPM", "V", "MA", "GS", "MS", "BAC", "WFC", "C", "SCHW",
                        "BLK"],
    "Healthcare":      ["JNJ", "UNH", "LLY", "PFE", "MRK", "ABBV", "TMO", "ABT",
                        "DHR", "AMGN"],
    "Energy":          ["XOM", "CVX", "COP", "SLB", "EOG", "OXY"],
    "Industrials":     ["CAT", "BA", "HON", "GE", "UPS", "LMT", "DE", "RTX"],
    "Staples":         ["PG", "KO", "PEP", "WMT", "COST", "MDLZ", "CL"],
    "Utilities":       ["NEE", "DUK", "SO", "AEP", "EXC"],
    "Materials":       ["LIN", "FCX", "SHW", "APD", "NEM", "DOW"],
    "Real Estate":     ["PLD", "AMT", "SPG", "EQIX", "O"],
}

SECTOR_ETF = {
    "Technology": "XLK", "Communication": "XLC", "Consumer Disc.": "XLY",
    "Financials": "XLF", "Healthcare": "XLV", "Energy": "XLE",
    "Industrials": "XLI", "Staples": "XLP", "Utilities": "XLU",
    "Materials": "XLB", "Real Estate": "XLRE",
}


HOT_STOCKS_BAN = frozenset({
    "NVDA", "MSFT", "TSLA", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "SPCX", "SPX"
})


def get_universe(name: str = "core", exclude_hot: bool = False) -> dict:
    raw = WIDE_UNIVERSE if str(name).lower() == "wide" else CORE_UNIVERSE
    if not exclude_hot:
        return raw
    filtered = {}
    for sec, tickers in raw.items():
        clean = [t for t in tickers if t.upper() not in HOT_STOCKS_BAN]
        if clean:
            filtered[sec] = clean
    return filtered
"""Build the frozen ETF snapshot (G1) from public sources.

Sources
-------
- ETF daily prices/volumes: Yahoo Finance chart API (adjusted close).
- Risk-free: Yahoo ``^IRX`` (13-week T-bill) because FRED was unreachable
  from this environment; the manifest records the substitution.
- Factors: Ken French Data Library (3-factor + momentum).

The script writes the logical tables used by the pipeline:
``prices``, ``returns``, ``etf_metadata``, ``universe``, ``factors``,
``risk_free``, ``benchmark``, plus ``MANIFEST.json``.

It never overwrites an existing snapshot unless ``--force`` is passed.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UNIVERSE = ROOT / "configs" / "etf_universe.csv"
DEFAULT_OUT = ROOT / "data" / "raw"

YAHOO_CHART = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    "?period1={start}&period2={end}&interval=1d"
    "&events=div%2Csplit&includeAdjustedClose=true"
)
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
FF3_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_Factors_CSV.zip"
)
FF_MOM_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Momentum_Factor_CSV.zip"
)


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Load a simple KEY=VALUE .env file without printing secrets."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)



def _request(url: str, *, retries: int = 4, timeout: int = 60) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 epistemic-dro/0.1"})
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(min(2.0 ** attempt, 10.0))
    raise RuntimeError(f"request failed after {retries} attempts: {last_error}") from last_error


def _json(url: str, *, retries: int = 4) -> dict:
    return json.loads(_request(url, retries=retries))


def _epoch(date: str) -> int:
    return int(pd.Timestamp(date, tz="UTC").timestamp())


def fetch_yahoo_monthly(
    ticker: str,
    start: str,
    end: str,
    *,
    retries: int = 4,
) -> tuple[pd.DataFrame, dict]:
    """Fetch daily bars and collapse them to month-end observations."""
    url = YAHOO_CHART.format(ticker=quote(ticker), start=_epoch(start), end=_epoch(end))
    payload = _json(url, retries=retries)
    chart = payload.get("chart") or {}
    if chart.get("error"):
        raise RuntimeError(f"Yahoo error for {ticker}: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise RuntimeError(f"Yahoo returned no result for {ticker}")

    result = results[0]
    meta = result.get("meta") or {}
    timestamps = result.get("timestamp") or []
    quote_data = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    adj_data = ((result.get("indicators") or {}).get("adjclose") or [{}])[0]
    closes = quote_data.get("close") or []
    volumes = quote_data.get("volume") or []
    adjcloses = adj_data.get("adjclose") or []

    if not timestamps or not closes:
        raise RuntimeError(f"Yahoo returned empty bars for {ticker}")

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
            "close": pd.to_numeric(pd.Series(closes), errors="coerce").to_numpy(),
            "volume": pd.to_numeric(pd.Series(volumes), errors="coerce").fillna(0.0).to_numpy(),
            "adj_close": pd.to_numeric(pd.Series(adjcloses), errors="coerce").to_numpy(),
        }
    )
    if frame["adj_close"].isna().all():
        frame["adj_close"] = frame["close"]
    frame = frame.dropna(subset=["date", "close", "adj_close"]).sort_values("date")
    if frame.empty:
        raise RuntimeError(f"no usable bars for {ticker}")
    frame["dollar_volume"] = frame["close"] * frame["volume"]

    monthly_rows: list[dict] = []
    for _period, group in frame.groupby(frame["date"].dt.to_period("M")):
        last = group.iloc[-1]
        monthly_rows.append(
            {
                "date": last["date"],
                "ticker": ticker,
                "close": float(last["close"]),
                "adj_close": float(last["adj_close"]),
                "volume": float(group["volume"].sum()),
                "dollar_volume": float(group["dollar_volume"].mean()),
            }
        )
    monthly = pd.DataFrame(monthly_rows)

    first_trade = meta.get("firstTradeDate")
    if first_trade:
        inception = pd.to_datetime(first_trade, unit="s", utc=True).tz_convert(None).normalize()
    else:
        inception = monthly["date"].min()
    meta_out = {
        "ticker": ticker,
        "name": meta.get("longName") or meta.get("shortName") or ticker,
        "inception_date": inception,
        "provider_first_trade_date": inception,
    }
    return monthly, meta_out


def build_risk_free_fred(api_key: str, start: str, end: str) -> pd.DataFrame:
    """Monthly risk-free return from FRED TB3MS (annualized percent)."""
    params = urlencode(
        {
            "series_id": "TB3MS",
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start,
            "observation_end": end,
        }
    )
    payload = _json(f"{FRED_API}?{params}")
    observations = payload.get("observations") or []
    rows = []
    for observation in observations:
        value = observation.get("value")
        if value in (None, "", "."):
            continue
        rows.append(
            {
                "date": pd.Timestamp(observation["date"]) + pd.offsets.MonthEnd(0),
                "rate_annual_pct": float(value),
            }
        )
    if not rows:
        raise RuntimeError("FRED returned no usable TB3MS observations")
    frame = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    frame["rf"] = (1.0 + frame["rate_annual_pct"] / 100.0) ** (1.0 / 12.0) - 1.0
    frame["source"] = "FRED:TB3MS"
    return frame


def build_risk_free_yahoo(start: str, end: str) -> pd.DataFrame:
    """Fallback: monthly risk-free return from Yahoo ^IRX."""
    daily, _ = fetch_yahoo_monthly("^IRX", start, end)
    daily = daily.rename(columns={"close": "rate_annual_pct"})[["date", "rate_annual_pct"]]
    daily["rf"] = (1.0 + daily["rate_annual_pct"] / 100.0) ** (1.0 / 12.0) - 1.0
    daily["source"] = "Yahoo:^IRX"
    return daily


def build_risk_free(start: str, end: str, api_key: str | None) -> tuple[pd.DataFrame, str | None]:
    """Use FRED when a key is available; otherwise record and use the fallback."""
    if api_key:
        try:
            return build_risk_free_fred(api_key, start, end), None
        except Exception as exc:  # noqa: BLE001 - recorded in the manifest
            reason = f"FRED TB3MS failed ({exc}); used Yahoo ^IRX fallback"
            print(f"warning: {reason}")
            return build_risk_free_yahoo(start, end), reason
    reason = "FRED_API_KEY not set; used Yahoo ^IRX fallback"
    print(f"warning: {reason}")
    return build_risk_free_yahoo(start, end), reason


def _read_ff_zip(url: str, header_token: str) -> pd.DataFrame:
    data = _request(url, retries=4)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        if not names:
            raise RuntimeError(f"empty zip: {url}")
        text = archive.read(names[0]).decode("latin-1")

    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(",") and header_token in stripped:
            header_index = index
            break
    if header_index is None:
        raise RuntimeError(f"could not find header {header_token!r} in {url}")

    rows: list[list[str]] = []
    for line in lines[header_index + 1 :]:
        if not line.strip():
            break
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2 or not parts[0].isdigit():
            break
        rows.append(parts)
    if not rows:
        raise RuntimeError(f"no monthly rows in {url}")

    frame = pd.DataFrame(rows)
    frame = frame.iloc[:, : 2]
    frame.columns = ["yyyymm", "value"]
    frame["date"] = pd.to_datetime(frame["yyyymm"], format="%Y%m") + pd.offsets.MonthEnd(0)
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame[["date", "value"]]


def build_factors(start: str, end: str) -> pd.DataFrame:
    data = _request(FF3_URL, retries=4)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        text = archive.read(archive.namelist()[0]).decode("latin-1")
    lines = text.splitlines()
    header = next(i for i, line in enumerate(lines) if "Mkt-RF" in line.replace(" ", ""))
    rows: list[list[str]] = []
    for line in lines[header + 1 :]:
        if not line.strip():
            break
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 5 or not parts[0].isdigit():
            break
        rows.append(parts[:5])
    ff3 = pd.DataFrame(rows, columns=["yyyymm", "mkt_rf", "smb", "hml", "rf"])
    ff3["date"] = pd.to_datetime(ff3["yyyymm"], format="%Y%m") + pd.offsets.MonthEnd(0)
    for column in ["mkt_rf", "smb", "hml", "rf"]:
        ff3[column] = pd.to_numeric(ff3[column], errors="coerce") / 100.0

    mom = _read_ff_zip(FF_MOM_URL, "Mom").rename(columns={"value": "mom"})
    mom["mom"] = mom["mom"] / 100.0

    factors = ff3[["date", "mkt_rf", "smb", "hml", "rf"]].merge(mom, on="date", how="inner")
    factors = factors[
        (factors["date"] >= pd.Timestamp(start)) & (factors["date"] <= pd.Timestamp(end))
    ]
    return factors.sort_values("date").reset_index(drop=True)


def build_universe(prices: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    """PIT eligibility: listed, >=36 months of history, price, and ADV floors."""
    rows: list[pd.DataFrame] = []
    min_history = 36
    min_price = 5.0
    min_adv = 1_000_000.0
    for date, snapshot in prices.groupby("date", sort=True):
        snap = snapshot[["ticker", "close", "dollar_volume"]].merge(
            metadata[["ticker", "inception_date"]], on="ticker", how="left"
        )
        inception = pd.to_datetime(snap["inception_date"])
        history_months = (date.year - inception.dt.year) * 12 + (date.month - inception.dt.month)
        snap["eligible"] = (
            (inception <= date)
            & (history_months >= min_history)
            & (snap["close"] >= min_price)
            & (snap["dollar_volume"] >= min_adv)
        )
        snap["date"] = date
        rows.append(snap[["date", "ticker", "eligible"]])
    return pd.concat(rows, ignore_index=True).sort_values(["date", "ticker"]).reset_index(drop=True)


def _display_path(path: Path) -> str:
    """Return a repo-relative path when possible, else the absolute path."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the frozen ETF snapshot.")
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--start", default="2004-01-01")
    parser.add_argument("--end", default="2025-01-01")
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--force", action="store_true", help="Overwrite an existing snapshot.")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "MANIFEST.json"
    if manifest_path.exists() and not args.force:
        raise SystemExit(
            f"{manifest_path} exists; pass --force to replace the frozen snapshot"
        )

    load_dotenv()
    fred_api_key = os.environ.get("FRED_API_KEY")
    if not fred_api_key:
        print("FRED_API_KEY not found in environment or .env; using ^IRX fallback.")

    universe = pd.read_csv(args.universe)
    required = {"ticker", "name", "category", "role"}
    if not required.issubset(universe.columns):
        raise SystemExit(f"universe file must contain {sorted(required)}")

    prices_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict] = []
    failed: dict[str, str] = {}

    print(f"Fetching {len(universe)} ETFs from Yahoo Finance...")
    for index, row in universe.iterrows():
        ticker = str(row["ticker"]).strip()
        try:
            monthly, meta = fetch_yahoo_monthly(ticker, args.start, args.end)
            prices_frames.append(monthly)
            meta.update(
                {
                    "name": str(row["name"]),
                    "category": str(row["category"]),
                    "role": str(row["role"]),
                    "expense_ratio": None,
                    "distribution_yield": None,
                    "underlying_index": None,
                    "metadata_vintage": "current_snapshot_unavailable",
                }
            )
            metadata_rows.append(meta)
            print(f"  [{index + 1:>3}/{len(universe)}] {ticker:6s} {len(monthly):>4} months")
        except Exception as exc:  # noqa: BLE001 - recorded in the manifest
            failed[ticker] = str(exc)
            print(f"  [{index + 1:>3}/{len(universe)}] {ticker:6s} FAILED: {exc}")
        time.sleep(args.sleep)

    if not prices_frames:
        raise SystemExit("no ETF data was fetched; snapshot not written")

    prices = pd.concat(prices_frames, ignore_index=True).sort_values(["date", "ticker"])
    metadata = pd.DataFrame(metadata_rows)
    metadata["inception_date"] = pd.to_datetime(metadata["inception_date"])

    returns = prices.sort_values(["ticker", "date"]).copy()
    returns["ret"] = returns.groupby("ticker")["adj_close"].pct_change()
    returns = returns.dropna(subset=["ret"])[["date", "ticker", "ret"]]

    risk_free, risk_free_fallback = build_risk_free(args.start, args.end, fred_api_key)
    returns = returns.merge(risk_free[["date", "rf"]], on="date", how="left")
    returns["excess_ret"] = returns["ret"] - returns["rf"]
    returns = returns[["date", "ticker", "ret", "excess_ret", "rf"]]

    factors = build_factors(args.start, args.end)
    universe_panel = build_universe(prices, metadata)

    benchmark = returns[returns["ticker"] == "SPY"][["date", "ret"]].rename(
        columns={"ret": "benchmark_ret"}
    )

    tables = {
        "prices": prices,
        "returns": returns,
        "etf_metadata": metadata,
        "universe": universe_panel,
        "factors": factors,
        "risk_free": risk_free,
        "benchmark": benchmark,
    }
    for name, frame in tables.items():
        path = args.out / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        print(f"wrote {_display_path(path)} ({len(frame)} rows)")

    manifest = {
        "dataset": "epistemic-dro-etf-monthly",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "Yahoo Finance chart API (adjusted close); Ken French Data Library; Yahoo ^IRX",
        "requested_start": args.start,
        "requested_end": args.end,
        "tickers_requested": int(len(universe)),
        "tickers_succeeded": int(len(metadata)),
        "tickers_failed": failed,
        "row_counts": {name: int(len(frame)) for name, frame in tables.items()},
        "sha256": {name: _sha256(args.out / f"{name}.parquet") for name in tables},
        "risk_free_source": str(risk_free["source"].iloc[0]),
        "risk_free_fallback": risk_free_fallback,
        "fred_api_key_used": bool(fred_api_key),
        "factor_source": "Ken French 3-factor + momentum, monthly decimals",
        "notes": [
            "Current-listed ETF universe; closed funds are not included. "
            "No survivorship-free claim.",
            "Expense ratio and distribution yield are unavailable and set to null; "
            "exclude them from the primary model.",
            "Inception date is Yahoo firstTradeDate where available, else the first observed bar.",
            "dollar_volume is average daily dollar volume within the month, not monthly total.",
        ],
        "source_urls": {"ff3": FF3_URL, "momentum": FF_MOM_URL, "yahoo": YAHOO_CHART},
        "universe_file": _display_path(args.universe),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {_display_path(manifest_path)}")
    print(f"succeeded {len(metadata)}/{len(universe)}; failed {len(failed)}")


if __name__ == "__main__":
    main()

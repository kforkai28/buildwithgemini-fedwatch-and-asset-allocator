"""Market and macroeconomic data tools for FedWatch & Asset Allocator."""
import os
from typing import Any, Dict, Optional
import urllib.request
import json
import yfinance as yf


def fetch_live_treasury_yields() -> Dict[str, Any]:
    """Fetches current US Treasury benchmark yields across the curve and calculates the 10Y-3M and 10Y-5Y spreads.
    
    Benchmarks retrieved:
      - 3-Month T-Bill (^IRX)
      - 5-Year Treasury Yield (^FVX)
      - 10-Year Treasury Yield (^TNX)
      - 30-Year Treasury Bond (^TYX)
      
    Returns:
        A dictionary with benchmark yields, calculated curve spreads, inversion status, and timestamp.
    """
    try:
        tickers = yf.Tickers("^IRX ^FVX ^TNX ^TYX")
        hist = tickers.history(period="5d")["Close"]
        
        if hist.empty:
            return {"error": "Failed to retrieve Treasury yields from market data feed."}

        latest_row = hist.iloc[-1]
        
        irx_3m = round(float(latest_row.get("^IRX", 0.0)), 3)
        fvx_5y = round(float(latest_row.get("^FVX", 0.0)), 3)
        tnx_10y = round(float(latest_row.get("^TNX", 0.0)), 3)
        tyx_30y = round(float(latest_row.get("^TYX", 0.0)), 3)

        # Spread calculations
        spread_10y_3m = round(tnx_10y - irx_3m, 3)
        spread_10y_5y = round(tnx_10y - fvx_5y, 3)
        
        curve_status = "inverted" if spread_10y_3m < 0 else "normal/steep"
        
        return {
            "status": "success",
            "benchmark_rates": {
                "3_month_tbill_pct": irx_3m,
                "5_year_treasury_pct": fvx_5y,
                "10_year_treasury_pct": tnx_10y,
                "30_year_treasury_pct": tyx_30y,
            },
            "yield_curve_spreads": {
                "10y_minus_3m_spread_bps": round(spread_10y_3m * 100, 1),
                "10y_minus_5y_spread_bps": round(spread_10y_5y * 100, 1),
                "curve_posture": curve_status,
            },
            "as_of_date": str(latest_row.name.date()) if hasattr(latest_row.name, "date") else str(latest_row.name),
            "summary": f"10Y Treasury stands at {tnx_10y}%, 3M T-bill at {irx_3m}%. The 10Y-3M spread is {spread_10y_3m}% ({curve_status}).",
        }
    except Exception as e:
        return {"error": f"Error fetching Treasury yields: {str(e)}"}


def fetch_fred_macro_series(series_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Optional add-on tool: Fetches official macroeconomic time-series from St. Louis Fed FRED API.
    
    Common series IDs:
      - 'T10Y2Y' (10-Year Treasury Constant Maturity Minus 2-Year Treasury)
      - 'FEDFUNDS' (Federal Funds Effective Rate)
      - 'PCEPILFE' (Core PCE Inflation YoY)
      - 'WALCL' (Federal Reserve Total Assets - Balance Sheet / QT)
      - 'UNRATE' (Civilian Unemployment Rate)
      
    Args:
        series_id: The FRED series identifier (e.g., 'T10Y2Y', 'FEDFUNDS', 'PCEPILFE').
        api_key: Optional API key. If omitted, will check FRED_API_KEY environment variable.
        
    Returns:
        Recent observations, units, and series metadata or informative setup instruction.
    """
    key = api_key or os.environ.get("FRED_API_KEY")
    if not key:
        return {
            "status": "api_key_required",
            "message": "FRED API requires a free API key from https://fred.stlouisfed.org/docs/api/api_key.html. Set the FRED_API_KEY environment variable or pass api_key parameter to enable this optional feature. Note: Core market yields are already available via fetch_live_treasury_yields() without an API key.",
            "series_requested": series_id
        }

    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={key}&file_type=json&sort_order=desc&limit=5"
        req = urllib.request.Request(url, headers={"User-Agent": "FedWatch-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            observations = data.get("observations", [])
            return {
                "status": "success",
                "series_id": series_id,
                "latest_observations": observations,
            }
    except Exception as e:
        return {"error": f"Failed to fetch FRED series '{series_id}': {str(e)}"}

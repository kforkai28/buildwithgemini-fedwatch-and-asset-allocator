"""Seed script for FedWatch & Asset Allocator Firestore database."""
from google.cloud import firestore

# Hardcoded project ID as string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-f13248a6578f"

db = firestore.Client(project=PROJECT_ID)

macro_indicators = [
    {
        "id": "fed_funds_rate",
        "name": "Federal Funds Target Rate",
        "category": "Interest Rates",
        "current_value": 5.375,
        "unit": "%",
        "trend": "neutral",
        "fomc_stance": "higher-for-longer",
        "last_updated": "2026-11-01",
        "summary": "Target range maintained at 5.25% - 5.50%. Committee monitoring labor market softening vs core services inflation.",
    },
    {
        "id": "10y_2y_yield_spread",
        "name": "10Y - 2Y Treasury Yield Spread",
        "category": "Yield Curve",
        "current_value": 0.15,
        "unit": "%",
        "trend": "steepening",
        "fomc_stance": "disinversion underway",
        "last_updated": "2026-11-10",
        "summary": "Curve disinverting as short rates price in easing while term premium returns to long-end yields.",
    },
    {
        "id": "core_pce_inflation",
        "name": "Core PCE Price Index YoY",
        "category": "Inflation",
        "current_value": 2.7,
        "unit": "%",
        "trend": "downward",
        "fomc_stance": "progressing toward 2% target",
        "last_updated": "2026-10-31",
        "summary": "Core PCE annualized rate declining gradually; housing services remaining somewhat sticky.",
    },
    {
        "id": "unemployment_rate",
        "name": "US Unemployment Rate (U-3)",
        "category": "Labor Market",
        "current_value": 4.1,
        "unit": "%",
        "trend": "stable",
        "fomc_stance": "balanced risk to mandate",
        "last_updated": "2026-11-03",
        "summary": "Labor market cooling to pre-pandemic normalization levels without broad-based layoffs.",
    },
]

portfolio_templates = [
    {
        "id": "conservative_income",
        "name": "Conservative Income & Capital Preservation",
        "risk_level": "low",
        "target_duration_years": 2.5,
        "allocation": {
            "cash_equivalents_tbills": 25,
            "short_duration_treasuries": 35,
            "intermediate_bonds": 20,
            "defensive_dividend_equities": 15,
            "gold_commodities": 5,
        },
        "description": "Favors cash and short-term Treasuries during restrictive Fed policy regimes.",
    },
    {
        "id": "balanced_growth",
        "name": "Balanced Multi-Asset Growth",
        "risk_level": "moderate",
        "target_duration_years": 4.5,
        "allocation": {
            "us_large_cap_equities": 40,
            "international_equities": 15,
            "core_aggregate_bonds": 30,
            "short_term_treasuries": 10,
            "real_assets": 5,
        },
        "description": "Standard 60/40 orientation with tactical cash buffer to absorb rate volatility.",
    },
    {
        "id": "aggressive_macro_momentum",
        "name": "Macro Momentum & Cyclical Growth",
        "risk_level": "high",
        "target_duration_years": 1.0,
        "allocation": {
            "technology_growth_equities": 50,
            "cyclical_small_cap": 20,
            "emerging_markets": 15,
            "high_yield_credit": 10,
            "cash_equivalents": 5,
        },
        "description": "High equity beta positioned for rate cut cycles and liquidity expansion.",
    },
]

def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    
    for item in macro_indicators:
        doc_id = item["id"]
        doc_ref = db.collection("macro_indicators").document(doc_id)
        doc_ref.set(item)
        print(f"Seeded macro_indicators/{doc_id}")
        
    for item in portfolio_templates:
        doc_id = item["id"]
        doc_ref = db.collection("portfolio_models").document(doc_id)
        doc_ref.set(item)
        print(f"Seeded portfolio_models/{doc_id}")
        
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed()

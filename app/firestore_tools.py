"""Firestore database tools for FedWatch & Asset Allocator."""
from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded project ID as string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-f13248a6578f"

_db: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client with the explicit string project ID."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def get_macro_indicator(indicator_id: str) -> Dict[str, Any]:
    """Retrieves current macroeconomic data and FOMC stance for a specific indicator.
    
    Args:
        indicator_id: The ID of the indicator (e.g., 'fed_funds_rate', '10y_2y_yield_spread', 
                      'core_pce_inflation', 'unemployment_rate').
                      
    Returns:
        A dictionary with the indicator details, value, trend, and summary.
    """
    db = get_firestore_client()
    doc = db.collection("macro_indicators").document(indicator_id).get()
    if not doc.exists:
        return {"error": f"Macro indicator '{indicator_id}' not found."}
    return doc.to_dict()


def list_macro_indicators() -> List[Dict[str, Any]]:
    """Lists all available macroeconomic indicators tracked in the database.
    
    Returns:
        A list of dictionaries with macro indicators and FOMC posture summaries.
    """
    db = get_firestore_client()
    docs = db.collection("macro_indicators").stream()
    return [doc.to_dict() for doc in docs]


def update_macro_indicator(
    indicator_id: str,
    current_value: float,
    trend: str,
    fomc_stance: str,
    summary: str
) -> Dict[str, Any]:
    """Updates or logs a macroeconomic indicator with new observation values and FOMC posture.
    
    Args:
        indicator_id: Unique indicator ID (e.g., 'fed_funds_rate', 'cpi_yoy').
        current_value: The numerical value (e.g. 5.25 for rate, 2.7 for inflation).
        trend: Directional movement (e.g., 'rising', 'falling', 'stable', 'steepening').
        fomc_stance: Interpretation relative to FOMC policy (e.g., 'restrictive', 'neutral', 'accommodative').
        summary: Qualitative explanation of the reading.
        
    Returns:
        Status confirmation dictionary.
    """
    db = get_firestore_client()
    doc_ref = db.collection("macro_indicators").document(indicator_id)
    payload = {
        "id": indicator_id,
        "current_value": current_value,
        "trend": trend,
        "fomc_stance": fomc_stance,
        "summary": summary
    }
    doc_ref.set(payload, merge=True)
    return {"status": "success", "message": f"Macro indicator '{indicator_id}' successfully updated."}


def get_portfolio_model(model_id: str) -> Dict[str, Any]:
    """Fetches an asset allocation portfolio template based on risk profile and macro posture.
    
    Args:
        model_id: ID of the portfolio model ('conservative_income', 'balanced_growth', 'aggressive_macro_momentum').
        
    Returns:
        Dictionary with asset class weights, target duration, and investment thesis.
    """
    db = get_firestore_client()
    doc = db.collection("portfolio_models").document(model_id).get()
    if not doc.exists:
        return {"error": f"Portfolio model '{model_id}' not found."}
    return doc.to_dict()


def list_portfolio_models() -> List[Dict[str, Any]]:
    """Lists all standard asset allocation portfolio models available in the system.
    
    Returns:
        A list of available portfolio allocation strategies.
    """
    db = get_firestore_client()
    docs = db.collection("portfolio_models").stream()
    return [doc.to_dict() for doc in docs]


def save_user_portfolio_allocation(
    user_id: str,
    portfolio_name: str,
    risk_level: str,
    allocations: Dict[str, float],
    notes: str
) -> Dict[str, Any]:
    """Saves or updates a user's customized asset allocation plan based on advisor recommendations.
    
    Args:
        user_id: Identifier for the user or session.
        portfolio_name: Label for the portfolio strategy.
        risk_level: Risk classification ('low', 'moderate', 'high').
        allocations: Dictionary of asset class percentages (e.g. {'equities': 60.0, 'treasuries': 30.0, 'cash': 10.0}).
        notes: Strategic notes and FOMC rationale.
        
    Returns:
        Status confirmation dictionary.
    """
    db = get_firestore_client()
    doc_ref = db.collection("user_portfolios").document(user_id)
    payload = {
        "user_id": user_id,
        "portfolio_name": portfolio_name,
        "risk_level": risk_level,
        "allocations": allocations,
        "notes": notes
    }
    doc_ref.set(payload, merge=True)
    return {"status": "success", "message": f"Portfolio for user '{user_id}' saved successfully."}

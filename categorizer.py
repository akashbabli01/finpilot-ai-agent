import sys
import os
import re
import pandas as pd

try:
    from llm import categorize_merchants_batched_llm
except ImportError:
    from finpilot.llm import categorize_merchants_batched_llm


# In-memory categorization cache {merchant_description: category}
_CATEGORIZATION_CACHE: dict[str, str] = {}

VALID_CATEGORIES = [
    "Rent", "Groceries", "Dining", "Transport", "Subscriptions",
    "Utilities", "Shopping", "Health", "Entertainment", "Income", "Other"
]

def keyword_fallback_category(description: str, txn_type: str = "debit") -> str:
    """
    Deterministic rule-based keyword fallback for merchant categorization.
    Ensures 100% demo reliability even without an API key or network access.
    """
    desc_lower = description.lower()

    if txn_type == "credit" or any(k in desc_lower for k in ["salary", "upwork", "freelance", "payout", "refund", "interest"]):
        return "Income"

    if any(k in desc_lower for k in ["rent", "landlord"]):
        return "Rent"

    if any(k in desc_lower for k in ["blinkit", "instamart", "zepto", "bigbasket", "supermarket", "grocery", "groceries", "mart"]):
        return "Groceries"

    if any(k in desc_lower for k in ["swiggy", "zomato", "starbucks", "coffee", "restaurant", "dining", "bar", "kitchen", "cafe", "third wave", "social"]):
        return "Dining"

    if any(k in desc_lower for k in ["uber", "ola", "fuel", "shell", "metro", "cab", "transport", "petrol", "parking"]):
        return "Transport"

    if any(k in desc_lower for k in ["netflix", "spotify", "cult.fit", "gym", "google one", "prime", "youtube", "apple.com/bill", "cloud storage"]):
        return "Subscriptions"

    if any(k in desc_lower for k in ["bescom", "electricity", "broadband", "airtel", "water", "bill", "utility", "power", "gas"]):
        return "Utilities"

    if any(k in desc_lower for k in ["croma", "amazon", "myntra", "decathlon", "uniqlo", "fashion", "store", "electronics", "shopping", "flipkart"]):
        return "Shopping"

    if any(k in desc_lower for k in ["apollo", "pharmacy", "1mg", "practo", "doctor", "health", "hospital", "clinic", "medical"]):
        return "Health"

    if any(k in desc_lower for k in ["movie", "cinema", "pvr", "inox", "entertainment", "ticket", "bookmyshow"]):
        return "Entertainment"

    return "Income" if txn_type == "credit" else "Other"

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorizes all transactions in DataFrame using batched LLM classification with keyword fallback.
    Caches categorized merchant descriptions to minimize API calls.
    """
    if df is None or df.empty:
        df_copy = df.copy() if df is not None else pd.DataFrame()
        df_copy['category'] = []
        return df_copy

    df_result = df.copy()

    # Find unique uncached merchant descriptions
    unique_merchants = df_result['description'].unique().tolist()
    uncached = [m for m in unique_merchants if m not in _CATEGORIZATION_CACHE]

    if uncached:
        # Attempt batched LLM call
        llm_results = categorize_merchants_batched_llm(uncached)
        if llm_results and isinstance(llm_results, dict):
            for merchant, cat in llm_results.items():
                if cat in VALID_CATEGORIES:
                    _CATEGORIZATION_CACHE[merchant] = cat

    # Apply cached categories or keyword fallback
    categories = []
    for _, row in df_result.iterrows():
        desc = row['description']
        t_type = row.get('type', 'debit')
        
        if desc in _CATEGORIZATION_CACHE:
            categories.append(_CATEGORIZATION_CACHE[desc])
        else:
            fallback = keyword_fallback_category(desc, t_type)
            _CATEGORIZATION_CACHE[desc] = fallback
            categories.append(fallback)

    df_result['category'] = categories
    return df_result

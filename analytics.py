import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_available_months(df: pd.DataFrame) -> list[str]:
    """Returns sorted list of 'YYYY-MM' strings present in the DataFrame."""
    if df is None or df.empty or 'date' not in df.columns:
        return []
    dates = pd.to_datetime(df['date'])
    return sorted(dates.dt.strftime('%Y-%m').unique().tolist())

def spend_by_category(df: pd.DataFrame, month: str = None) -> dict[str, float]:
    """
    Returns spending total per category for debit transactions.
    If month is provided (e.g., '2026-09'), filters transactions for that month.
    """
    if df is None or df.empty:
        return {}

    filtered = df[df['type'] == 'debit'].copy()
    if month:
        filtered = filtered[filtered['date'].str.startswith(month)]

    if filtered.empty:
        return {}

    grouped = filtered.groupby('category')['amount'].sum().round(2)
    return grouped.to_dict()

def monthly_summary(df: pd.DataFrame, month: str = None) -> dict:
    """
    Returns summary metrics: income, expenses, net savings, savings rate %, top 3 categories.
    """
    if df is None or df.empty:
        return {
            "month": month or "All",
            "income": 0.0,
            "expenses": 0.0,
            "net_savings": 0.0,
            "savings_rate_pct": 0.0,
            "top_categories": {}
        }

    filtered = df.copy()
    if month:
        filtered = filtered[filtered['date'].str.startswith(month)]

    income = round(float(filtered[filtered['type'] == 'credit']['amount'].sum()), 2)
    expenses = round(float(filtered[filtered['type'] == 'debit']['amount'].sum()), 2)
    net_savings = round(income - expenses, 2)
    savings_rate = round((net_savings / income * 100), 1) if income > 0 else 0.0

    category_spend = spend_by_category(filtered)
    sorted_cats = dict(sorted(category_spend.items(), key=lambda item: item[1], reverse=True)[:5])

    return {
        "month": month or "All Time",
        "income": income,
        "expenses": expenses,
        "net_savings": net_savings,
        "savings_rate_pct": savings_rate,
        "top_categories": sorted_cats
    }

def compare_months(df: pd.DataFrame, month_a: str, month_b: str) -> dict:
    """
    Compares category spending between month_a and month_b.
    Returns delta (₹) and percentage change (%).
    """
    if df is None or df.empty:
        return {}

    spend_a = spend_by_category(df, month_a)
    spend_b = spend_by_category(df, month_b)

    all_categories = sorted(list(set(spend_a.keys()).union(set(spend_b.keys()))))
    comparison = {}

    for cat in all_categories:
        val_a = spend_a.get(cat, 0.0)
        val_b = spend_b.get(cat, 0.0)
        abs_change = round(val_b - val_a, 2)
        
        if val_a > 0:
            pct_change = round(((val_b - val_a) / val_a) * 100, 1)
        elif val_b > 0:
            pct_change = 100.0
        else:
            pct_change = 0.0

        comparison[cat] = {
            "month_a_spend": val_a,
            "month_b_spend": val_b,
            "abs_change": abs_change,
            "pct_change": pct_change
        }

    total_a = sum(spend_a.values())
    total_b = sum(spend_b.values())
    total_abs_change = round(total_b - total_a, 2)
    total_pct_change = round(((total_b - total_a) / total_a) * 100, 1) if total_a > 0 else (100.0 if total_b > 0 else 0.0)

    return {
        "month_a": month_a,
        "month_b": month_b,
        "total_spend_month_a": round(total_a, 2),
        "total_spend_month_b": round(total_b, 2),
        "total_abs_change": total_abs_change,
        "total_pct_change": total_pct_change,
        "category_comparison": comparison
    }

def detect_subscriptions(df: pd.DataFrame) -> list[dict]:
    """
    Identifies recurring subscription/bill payments:
    - Same description/merchant
    - Similar amount (within ±15%)
    - Roughly monthly interval (20 to 38 days apart) across >= 2 occurrences
    """
    if df is None or df.empty:
        return []

    debits = df[df['type'] == 'debit'].copy()
    if debits.empty:
        return []

    debits['dt'] = pd.to_datetime(debits['date'])
    subscriptions = []

    # Group by merchant description
    grouped = debits.groupby('description')

    for merchant, group in grouped:
        if len(group) < 2:
            continue

        sorted_group = group.sort_values(by='dt')
        amounts = sorted_group['amount'].values
        dates = sorted_group['dt'].values

        # Check amount stability: relative difference <= 15%
        avg_amount = np.mean(amounts)
        if avg_amount == 0:
            continue
        max_dev = np.max(np.abs(amounts - avg_amount)) / avg_amount
        
        if max_dev <= 0.15:
            # Check intervals between consecutive transactions
            diffs = [(dates[i+1] - dates[i]) / np.timedelta64(1, 'D') for i in range(len(dates)-1)]
            
            # Check if majority of intervals are roughly monthly (20-38 days)
            valid_intervals = [d for d in diffs if 20 <= d <= 38]
            if len(valid_intervals) >= 1:
                last_dt = pd.to_datetime(dates[-1])
                avg_interval_days = int(np.mean(valid_intervals)) if valid_intervals else 30
                next_expected = last_dt + timedelta(days=avg_interval_days)

                subscriptions.append({
                    "merchant": merchant,
                    "category": sorted_group['category'].iloc[0] if 'category' in sorted_group.columns else "Subscriptions",
                    "monthly_amount": round(float(avg_amount), 2),
                    "occurrences": len(sorted_group),
                    "last_date": last_dt.strftime('%Y-%m-%d'),
                    "next_expected_date": next_expected.strftime('%Y-%m-%d')
                })

    return subscriptions

def upcoming_obligations(df: pd.DataFrame, days: int = 30) -> list[dict]:
    """
    Projects recurring subscription and bill obligations due in the next N days
    starting from the latest transaction date in df.
    """
    subs = detect_subscriptions(df)
    if not subs or df is None or df.empty:
        return []

    latest_date_str = df['date'].max()
    latest_dt = pd.to_datetime(latest_date_str)
    cutoff_dt = latest_dt + timedelta(days=days)

    upcoming = []
    for sub in subs:
        next_dt = pd.to_datetime(sub['next_expected_date'])
        if latest_dt <= next_dt <= cutoff_dt:
            days_until = (next_dt - latest_dt).days
            upcoming.append({
                "merchant": sub['merchant'],
                "category": sub['category'],
                "amount": sub['monthly_amount'],
                "expected_date": next_dt.strftime('%Y-%m-%d'),
                "days_until": int(days_until)
            })

    upcoming.sort(key=lambda x: x['expected_date'])
    return upcoming

def detect_anomalies(df: pd.DataFrame) -> list[dict]:
    """
    Detects transactions where amount > category_mean + 2 * category_std.
    """
    if df is None or df.empty or 'category' not in df.columns:
        return []

    debits = df[df['type'] == 'debit'].copy()
    if debits.empty:
        return []

    anomalies = []
    cat_groups = debits.groupby('category')

    for cat, group in cat_groups:
        if len(group) < 3:
            continue
        
        mean_val = group['amount'].mean()
        std_val = group['amount'].std()

        if pd.isna(std_val) or std_val == 0:
            continue

        threshold = mean_val + 2 * std_val

        for _, row in group.iterrows():
            if row['amount'] > threshold:
                anomalies.append({
                    "date": row['date'],
                    "description": row['description'],
                    "category": cat,
                    "amount": round(float(row['amount']), 2),
                    "category_mean": round(float(mean_val), 2),
                    "threshold": round(float(threshold), 2),
                    "excess_amount": round(float(row['amount'] - mean_val), 2)
                })

    anomalies.sort(key=lambda x: x['date'], reverse=True)
    return anomalies

def budget_status(df: pd.DataFrame, month: str, budgets: dict[str, float]) -> dict:
    """
    Compares spent vs budget limit per category for specified month.
    Also calculates committed recurring obligations for remaining days in the month.
    """
    if df is None or df.empty or not budgets:
        return {}

    spent_dict = spend_by_category(df, month)
    upcoming = upcoming_obligations(df, days=30)
    
    # Committed amounts per category
    committed_dict = {}
    for item in upcoming:
        if item['expected_date'].startswith(month):
            c_cat = item['category']
            committed_dict[c_cat] = committed_dict.get(c_cat, 0.0) + item['amount']

    result = {}
    for cat, budget in budgets.items():
        if budget <= 0:
            continue
        spent = spent_dict.get(cat, 0.0)
        committed = committed_dict.get(cat, 0.0)
        total_encumbered = spent + committed
        remaining = budget - spent
        pct_spent = round((spent / budget) * 100, 1)

        result[cat] = {
            "budget": round(budget, 2),
            "spent": round(spent, 2),
            "committed_upcoming": round(committed, 2),
            "total_encumbered": round(total_encumbered, 2),
            "remaining": round(remaining, 2),
            "pct_spent": pct_spent,
            "over_budget": spent > budget
        }

    return result

def goal_projection(df: pd.DataFrame, goal_amount: float, target_date_str: str, current_savings: float) -> dict:
    """
    Projects if user can achieve savings goal given target_date and current_savings.
    Uses historical average monthly net savings across available full months.
    """
    if df is None or df.empty:
        return {"error": "No transaction data available"}

    months = get_available_months(df)
    if not months:
        return {"error": "Invalid date range in data"}

    # Calculate average monthly savings
    monthly_savings = []
    for m in months:
        summary = monthly_summary(df, m)
        monthly_savings.append(summary['net_savings'])

    avg_monthly_savings = round(float(np.mean(monthly_savings)), 2) if monthly_savings else 0.0

    latest_date = pd.to_datetime(df['date'].max())
    try:
        target_date = pd.to_datetime(target_date_str)
    except Exception:
        target_date = latest_date + timedelta(days=365)

    days_remaining = max(1, (target_date - latest_date).days)
    months_remaining = max(0.1, days_remaining / 30.4375)

    target_needed = max(0.0, goal_amount - current_savings)
    required_monthly_savings = round(target_needed / months_remaining, 2)

    on_track = avg_monthly_savings >= required_monthly_savings
    monthly_deficit_surplus = round(avg_monthly_savings - required_monthly_savings, 2)

    # Projected reach date
    if avg_monthly_savings > 0 and target_needed > 0:
        months_to_reach = target_needed / avg_monthly_savings
        projected_reach_date = (latest_date + timedelta(days=int(months_to_reach * 30.4375))).strftime('%Y-%m-%d')
    elif target_needed <= 0:
        projected_reach_date = latest_date.strftime('%Y-%m-%d')
    else:
        projected_reach_date = "N/A (Savings rate <= 0)"

    return {
        "goal_amount": float(goal_amount),
        "current_savings": float(current_savings),
        "target_needed": round(target_needed, 2),
        "target_date": target_date.strftime('%Y-%m-%d'),
        "months_remaining": round(months_remaining, 1),
        "avg_monthly_savings": avg_monthly_savings,
        "required_monthly_savings": required_monthly_savings,
        "monthly_deficit_surplus": monthly_deficit_surplus,
        "on_track": bool(on_track),
        "projected_reach_date": projected_reach_date
    }

def calculate_financial_health_score(df: pd.DataFrame, month: str = None, budgets: dict = None) -> dict:
    """
    Calculates a comprehensive Financial Health Score (0 - 100) based on:
    - Savings Rate (30 pts)
    - Budget Adherence (30 pts)
    - Subscription Load Ratio (20 pts)
    - Anomaly / Impulse Spend Ratio (20 pts)
    """
    if df is None or df.empty:
        return {"score": 50, "rating": "Moderate", "breakdown": {}}

    summary = monthly_summary(df, month)
    income = summary["income"]
    expenses = summary["expenses"]
    savings_rate = summary["savings_rate_pct"]

    # 1. Savings Rate Score (Max 30)
    # 20%+ savings rate gets full 30 pts; 0% gets 0 pts
    sr_score = min(30.0, max(0.0, (savings_rate / 25.0) * 30.0))

    # 2. Budget Adherence Score (Max 30)
    if budgets:
        b_status = budget_status(df, month or get_available_months(df)[-1], budgets)
        over_count = sum(1 for b in b_status.values() if b["over_budget"])
        total_b = max(1, len(b_status))
        b_score = round(max(0.0, (1 - (over_count / total_b)) * 30.0), 1)
    else:
        b_score = 25.0

    # 3. Subscription Load Score (Max 20)
    # Subscriptions > 20% of income penalizes score
    subs = detect_subscriptions(df)
    sub_monthly = sum(s["monthly_amount"] for s in subs)
    sub_ratio = (sub_monthly / income) if income > 0 else 0.1
    sub_score = round(max(0.0, min(20.0, (1.0 - max(0.0, sub_ratio - 0.05) / 0.20) * 20.0)), 1)

    # 4. Anomaly Penalty Score (Max 20)
    anomalies = detect_anomalies(df)
    anom_count = len(anomalies)
    anom_score = round(max(0.0, 20.0 - (anom_count * 5.0)), 1)

    total_score = int(round(sr_score + b_score + sub_score + anom_score))
    total_score = max(0, min(100, total_score))

    if total_score >= 80:
        rating = "Excellent 🟢"
    elif total_score >= 65:
        rating = "Good 🟡"
    elif total_score >= 50:
        rating = "Fair 🟠"
    else:
        rating = "Needs Attention 🔴"

    return {
        "score": total_score,
        "rating": rating,
        "breakdown": {
            "savings_rate_score": round(sr_score, 1),
            "budget_adherence_score": round(b_score, 1),
            "subscription_load_score": round(sub_score, 1),
            "anomaly_score": round(anom_score, 1)
        }
    }

def get_daily_cash_flow(df: pd.DataFrame, month: str = None) -> pd.DataFrame:
    """Returns daily income, expenses, and net cumulative cash flow over time."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "income", "expenses", "net", "cumulative_net"])

    filtered = df.copy()
    if month:
        filtered = filtered[filtered['date'].str.startswith(month)]

    if filtered.empty:
        return pd.DataFrame(columns=["date", "income", "expenses", "net", "cumulative_net"])

    pivoted = filtered.groupby(['date', 'type'])['amount'].sum().unstack(fill_value=0.0).reset_index()
    if 'credit' not in pivoted.columns:
        pivoted['credit'] = 0.0
    if 'debit' not in pivoted.columns:
        pivoted['debit'] = 0.0

    pivoted = pivoted.rename(columns={'credit': 'income', 'debit': 'expenses'})
    pivoted['net'] = pivoted['income'] - pivoted['expenses']
    pivoted['cumulative_net'] = pivoted['net'].cumsum()
    return pivoted.sort_values(by='date').reset_index(drop=True)

def search_transactions(df: pd.DataFrame, query: str = None, category: str = None, min_amt: float = None, max_amt: float = None) -> list[dict]:
    """Filters transactions by merchant search string, category, or min/max amount."""
    if df is None or df.empty:
        return []

    res = df.copy()
    if query:
        res = res[res['description'].str.lower().str.contains(query.lower())]
    if category and category != "All":
        res = res[res['category'] == category]
    if min_amt is not None:
        res = res[res['amount'] >= min_amt]
    if max_amt is not None:
        res = res[res['amount'] <= max_amt]

    return res.sort_values(by='date', ascending=False).to_dict(orient='records')

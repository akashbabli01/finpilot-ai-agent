import os
import sys
import json
import pandas as pd

# Support both relative and absolute imports
try:
    from llm import call_llm_chat
    import analytics
except ImportError:
    from finpilot.llm import call_llm_chat
    from finpilot import analytics

# Financial advice disclaimer prompt prefix
SYSTEM_PROMPT = """You are FinPilot, an AI personal finance decision-support agent for transaction analysis.

CRITICAL RULES:
1. NEVER perform mathematical calculations or estimate numbers yourself. All numerical data, totals, deltas, anomalies, subscription dates, and goal projections MUST come directly from calling your financial analytics tools.
2. You must call the appropriate tool(s) to fetch accurate figures before answering the user's question.
3. Keep your answers clear, concise, well-structured, and easy to read with bullet points where appropriate. Format amounts clearly in INR (₹).
4. DISCLAIMER: You DO NOT provide investment or financial advice. You strictly assist users in understanding their historical transaction data.
"""

# Tool schemas definitions for Anthropic Claude API
TOOLS = [
    {
        "name": "spend_by_category",
        "description": "Calculates total expenditure per category for debit transactions in a specific month or all time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "Target month in YYYY-MM format, e.g. '2026-09'. If omitted, computes all-time total."}
            }
        }
    },
    {
        "name": "monthly_summary",
        "description": "Calculates total income, total expenses, net savings, savings rate %, and top spending categories for a given month.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "Target month in YYYY-MM format, e.g. '2026-09'. If omitted, computes overall summary."}
            }
        }
    },
    {
        "name": "compare_months",
        "description": "Compares spending category by category between two months (e.g., month_a vs month_b), returning absolute and percentage changes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month_a": {"type": "string", "description": "Baseline month in YYYY-MM format, e.g. '2026-08'"},
                "month_b": {"type": "string", "description": "Comparison month in YYYY-MM format, e.g. '2026-09'"}
            },
            "required": ["month_a", "month_b"]
        }
    },
    {
        "name": "detect_subscriptions",
        "description": "Identifies recurring subscription and bill payments, monthly cost, last payment date, and next expected payment date.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "upcoming_obligations",
        "description": "Projects recurring subscription and bill payments expected in the next N days.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Number of projection days, default 30"}
            }
        }
    },
    {
        "name": "detect_anomalies",
        "description": "Detects unusual spending spikes exceeding category mean + 2 standard deviations.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "budget_status",
        "description": "Calculates category expenditure vs budget limits and encumbered committed recurring payments for a month.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "Target month in YYYY-MM format, e.g. '2026-09'"}
            },
            "required": ["month"]
        }
    },
    {
        "name": "goal_projection",
        "description": "Projects if the user can reach their savings goal given goal amount, target date, current savings, and historical savings rate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "goal_amount": {"type": "number", "description": "Target goal amount in INR"},
                "target_date": {"type": "string", "description": "Target completion date in YYYY-MM-DD"},
                "current_savings": {"type": "number", "description": "Current accumulated savings in INR"}
            }
        }
    },
    {
        "name": "calculate_financial_health_score",
        "description": "Calculates overall Financial Health Score (0-100) based on savings rate, budget adherence, subscription load, and anomalies.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "Target month in YYYY-MM format, e.g. '2026-09'"}
            }
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict, df: pd.DataFrame, budgets: dict = None, goal_info: dict = None):
    """Executes pure pandas analytics function corresponding to the tool_name."""
    if budgets is None:
        budgets = {"Groceries": 20000, "Dining": 10000, "Transport": 8000, "Shopping": 15000}
    if goal_info is None:
        goal_info = {"goal_amount": 100000.0, "target_date": "2026-12-31", "current_savings": 25000.0}

    latest_month = analytics.get_available_months(df)[-1] if df is not None and not df.empty else "2026-09"
    months = analytics.get_available_months(df)

    if tool_name == "spend_by_category":
        month = tool_input.get("month", latest_month)
        return analytics.spend_by_category(df, month)

    elif tool_name == "monthly_summary":
        month = tool_input.get("month", latest_month)
        return analytics.monthly_summary(df, month)

    elif tool_name == "compare_months":
        month_a = tool_input.get("month_a")
        month_b = tool_input.get("month_b", latest_month)
        if not month_a:
            month_a = months[-2] if len(months) >= 2 else month_b
        return analytics.compare_months(df, month_a, month_b)

    elif tool_name == "detect_subscriptions":
        return analytics.detect_subscriptions(df)

    elif tool_name == "upcoming_obligations":
        days = tool_input.get("days", 30)
        return analytics.upcoming_obligations(df, days)

    elif tool_name == "detect_anomalies":
        return analytics.detect_anomalies(df)

    elif tool_name == "budget_status":
        month = tool_input.get("month", latest_month)
        return analytics.budget_status(df, month, budgets)

    elif tool_name == "goal_projection":
        g_amt = tool_input.get("goal_amount", goal_info.get("goal_amount", 100000.0))
        t_date = tool_input.get("target_date", goal_info.get("target_date", "2026-12-31"))
        c_sav = tool_input.get("current_savings", goal_info.get("current_savings", 25000.0))
        return analytics.goal_projection(df, g_amt, t_date, c_sav)

    elif tool_name == "calculate_financial_health_score":
        month = tool_input.get("month", latest_month)
        return analytics.calculate_financial_health_score(df, month, budgets)

    else:
        return {"error": f"Unknown tool: {tool_name}"}

def run_agent_turn(user_query: str, chat_history: list, df: pd.DataFrame, budgets: dict = None, goal_info: dict = None) -> str:
    """
    Executes a tool-calling chat turn with Anthropic Claude API or keyword fallback executor.
    """
    if df is None or df.empty:
        return "Please upload a transaction CSV or click 'Use Sample Data' in the sidebar to start asking questions."

    if budgets is None:
        budgets = {"Groceries": 20000, "Dining": 10000, "Transport": 8000, "Shopping": 15000}
    if goal_info is None:
        goal_info = {"goal_amount": 100000.0, "target_date": "2026-12-31", "current_savings": 25000.0}

    # Format Anthropic API messages payload
    messages = []
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_query})

    # Attempt LLM tool-calling execution loop
    response = call_llm_chat(messages=messages, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

    if response:
        # Loop for handling tool calls
        while response and getattr(response, "stop_reason", None) == "tool_use":
            # Extract tool call blocks
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            if not tool_calls:
                break

            # Append assistant message with content blocks to message history
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call
            tool_results_content = []
            for tc in tool_calls:
                t_name = tc.name
                t_input = tc.input
                t_id = tc.id

                # Execute pure pandas analytics tool
                t_result = execute_tool(t_name, t_input, df, budgets, goal_info)

                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": t_id,
                    "content": json.dumps(t_result)
                })

            # Append tool results as user message payload
            messages.append({"role": "user", "content": tool_results_content})

            # Call Claude with tool outputs
            response = call_llm_chat(messages=messages, tools=TOOLS, system_prompt=SYSTEM_PROMPT)

        if response and response.content:
            text_blocks = [b.text for b in response.content if b.type == "text"]
            if text_blocks:
                return "\n".join(text_blocks)

    # Deterministic Fallback Executor if API key missing or network unavailable
    return fallback_query_executor(user_query, df, budgets, goal_info)

def fallback_query_executor(query: str, df: pd.DataFrame, budgets: dict = None, goal_info: dict = None) -> str:
    """
    Deterministic rule-based fallback tool executor to ensure 100% working demo without API key.
    Calculates numbers strictly using analytics.py.
    """
    if budgets is None:
        budgets = {"Groceries": 20000, "Dining": 10000, "Transport": 8000, "Shopping": 15000}
    if goal_info is None:
        goal_info = {"goal_amount": 100000.0, "target_date": "2026-12-31", "current_savings": 25000.0}
    q_lower = query.lower()
    months = analytics.get_available_months(df)
    latest_m = months[-1] if months else "2026-09"
    prev_m = months[-2] if len(months) >= 2 else latest_m

    if any(k in q_lower for k in ["most", "highest", "top spend", "where did i spend"]):
        spend = analytics.spend_by_category(df, latest_m)
        if not spend:
            return f"No spending records found for {latest_m}."
        top_cat = max(spend.items(), key=lambda x: x[1])
        summary = analytics.monthly_summary(df, latest_m)
        return (
            f"**Spending Breakdown for {latest_m}:**\n"
            f"- Your highest spending category was **{top_cat[0]}** at **₹{top_cat[1]:,.2f}**.\n"
            f"- Total expenses for {latest_m}: **₹{summary['expenses']:,.2f}** across all categories.\n"
            f"- Top categories: " + ", ".join([f"{c}: ₹{v:,.2f}" for c, v in summary['top_categories'].items()])
        )

    elif any(k in q_lower for k in ["subscription", "subscriptions", "recurring"]):
        subs = analytics.detect_subscriptions(df)
        if not subs:
            return "No active recurring subscriptions detected in your transaction history."
        lines = [f"**Detected Recurring Subscriptions ({len(subs)} found):**"]
        for s in subs:
            lines.append(f"- **{s['merchant']}** ({s['category']}): **₹{s['monthly_amount']:,.2f}/mo** | Last paid: {s['last_date']} | Next due: {s['next_expected_date']}")
        return "\n".join(lines)

    elif any(k in q_lower for k in ["increased", "compare", "month-over-month", "higher than last"]):
        comp = analytics.compare_months(df, prev_m, latest_m)
        lines = [f"**Month-over-Month Comparison ({prev_m} vs {latest_m}):**"]
        lines.append(f"- Total spending change: **₹{comp['total_abs_change']:+,.2f}** ({comp['total_pct_change']:+.1f}%)\n")
        lines.append("**Category Increases:**")
        increased = {cat: data for cat, data in comp['category_comparison'].items() if data['abs_change'] > 0}
        for cat, data in sorted(increased.items(), key=lambda x: x[1]['abs_change'], reverse=True):
            lines.append(f"- **{cat}**: +₹{data['abs_change']:,.2f} (+{data['pct_change']:.1f}%) | {prev_m}: ₹{data['month_a_spend']:,.2f} ➔ {latest_m}: ₹{data['month_b_spend']:,.2f}")
        return "\n".join(lines)

    elif any(k in q_lower for k in ["budget", "committed", "encumbered"]):
        b_status = analytics.budget_status(df, latest_m, budgets)
        if not b_status:
            return "No active budget limits configured."
        lines = [f"**Budget Status & Committed Obligations for {latest_m}:**"]
        total_committed = 0.0
        for cat, b in b_status.items():
            lines.append(f"- **{cat}**: Spent ₹{b['spent']:,.2f} of ₹{b['budget']:,.2f} budget ({b['pct_spent']}%) | Committed upcoming: ₹{b['committed_upcoming']:,.2f}")
            total_committed += b['committed_upcoming']
        lines.append(f"\nTotal upcoming committed recurring bills for this month: **₹{total_committed:,.2f}**")
        return "\n".join(lines)

    elif any(k in q_lower for k in ["health", "score", "rating", "financial health"]):
        h_score = analytics.calculate_financial_health_score(df, latest_m, budgets)
        bd = h_score["breakdown"]
        return (
            f"**Financial Health Score for {latest_m}:** {h_score['score']}/100 ({h_score['rating']})\n"
            f"- **Savings Rate Score:** {bd['savings_rate_score']}/30 pts\n"
            f"- **Budget Adherence Score:** {bd['budget_adherence_score']}/30 pts\n"
            f"- **Subscription Load Score:** {bd['subscription_load_score']}/20 pts\n"
            f"- **Anomaly Penalty Score:** {bd['anomaly_score']}/20 pts\n\n"
            f"*Tip: Improve your score by staying within category budgets and reviewing unused subscriptions.*"
        )

    elif any(k in q_lower for k in ["goal", "savings goal", "on track", "reach"]):
        proj = analytics.goal_projection(
            df,
            goal_info.get("goal_amount", 100000.0),
            goal_info.get("target_date", "2026-12-31"),
            goal_info.get("current_savings", 25000.0)
        )
        status_str = "✅ **ON TRACK**" if proj["on_track"] else "⚠️ **OFF TRACK**"
        return (
            f"**Savings Goal Status:** {status_str}\n"
            f"- Target Goal: **₹{proj['goal_amount']:,.2f}** by {proj['target_date']}\n"
            f"- Current Savings: **₹{proj['current_savings']:,.2f}** (Remaining: ₹{proj['target_needed']:,.2f})\n"
            f"- Historical Avg Monthly Net Savings: **₹{proj['avg_monthly_savings']:,.2f}**\n"
            f"- Required Monthly Savings: **₹{proj['required_monthly_savings']:,.2f}**\n"
            f"- Monthly Deficit/Surplus: **₹{proj['monthly_deficit_surplus']:+,.2f}**\n"
            f"- Projected Goal Completion Date: **{proj['projected_reach_date']}**"
        )

    else:
        summary = analytics.monthly_summary(df, latest_m)
        return (
            f"**Financial Overview for {latest_m}:**\n"
            f"- Income: **₹{summary['income']:,.2f}**\n"
            f"- Expenses: **₹{summary['expenses']:,.2f}**\n"
            f"- Net Savings: **₹{summary['net_savings']:,.2f}** ({summary['savings_rate_pct']}% savings rate)\n"
            f"- Top Spend Category: **{list(summary['top_categories'].keys())[0]}** (₹{list(summary['top_categories'].values())[0]:,.2f})\n"
            f"\n*You can ask specific questions about subscriptions, budget commitments, anomalies, or savings goals!*"
        )

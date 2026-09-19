# ✈️ FinPilot - Personal Finance Decision-Support Agent

FinPilot is a demo-ready personal finance decision-support agent built for AI Agent Hackathons. It ingests bank and credit card transaction CSVs, normalizes and categorizes spending, detects recurring subscriptions, flags unusual spending anomalies, monitors category budgets, projects savings goals, and provides a natural language chat interface powered by Anthropic Claude tool calling.

> ⚠️ **IMPORTANT DISCLAIMER**: FinPilot is strictly an informational decision-support and data visualization tool. It **DOES NOT** provide investment, tax, legal, or formal financial advice.

---

## 🏗️ Architecture Diagram

```
+-----------------------------------------------------------------------+
|                            Streamlit UI                               |
| (Sidebar, Overview, Subscriptions, Insights/Goals, Chat, Reports)     |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------+-----------------------------------+
|               Categorization & CSV Processing Layer                    |
|   processing.py (Normalize CSV)  <--->  categorizer.py (LLM + Rules)   |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------+-----------------------------------+
|                 Pure Pandas Analytics Engine                          |
|   analytics.py (Summary, MoM, Subscriptions, Anomalies, Goals)        |
+-----------------------------------+-----------------------------------+
                                    |
                +-------------------+-------------------+
                |                                       |
                v                                       v
+---------------+---------------+       +---------------+---------------+
|    LLM Agent (agent.py)       |       |   Anthropic Claude API Wrapper |
| Tool-Calling Execution Loop   | <---> |   llm.py (Claude 3.5 Sonnet)  |
+-------------------------------+       +-------------------------------+
```

---

## ⚡ Quickstart Setup

1. **Clone repository & navigate to directory:**
   ```bash
   cd finpilot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (Optional):**
   Copy `.env.example` to `.env` and set your API key:
   ```bash
   cp .env.example .env
   ```
   *Note: If no API key is provided, FinPilot automatically falls back to deterministic rule engine mode so the demo never breaks!*

4. **Run Application:**
   ```bash
   streamlit run app.py
   ```

5. **Run Unit Tests:**
   ```bash
   pytest tests/test_analytics.py
   ```

---

## ⏱️ 60-Second Hackathon Demo Script

1. **Launch App**: Open `http://localhost:8501`.
2. **Load Sample Data**: Click **"📊 Use Sample Data (~250 txns)"** in the left sidebar.
3. **Explore Overview Tab**: Show total income (₹1.57L), expenses (₹1.69L), and interactive Plotly category pie/bar charts.
4. **Explore Subscriptions Tab**: Highlight auto-detected recurring subscriptions (Netflix, Spotify, Cult.fit Gym, Google One, HDFC Rent) and upcoming 30-day timeline.
5. **Explore Insights Tab**: Show MoM comparison (Shopping & Dining spend increase) and the flagged **₹58,500 Croma Electronics anomaly spike**.
6. **Chat with FinPilot Agent**: Switch to **"💬 Ask FinPilot"** tab and click or type the key questions:
   - *"Where did I spend the most this month?"*
   - *"Which subscriptions am I paying for?"*
   - *"What expenses increased compared with last month?"*
   - *"How much of my budget is already committed?"*
   - *"Can I reach my savings goal at this rate?"*
7. **Generate Executive Report**: Go to **"📄 Monthly Report"**, click **"Generate Monthly Report"**, and download the synthesized `.md` report.

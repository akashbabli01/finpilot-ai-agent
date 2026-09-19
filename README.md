FinPilot

An autonomous AI agent for personal finance — Agentic AI Hackathon (Product Space)

Team: Synapse Squad

FinPilot is an AI agent, not just a dashboard: it ingests raw bank/credit card CSV exports, reasons over the transactions using Claude, and takes action on your behalf — categorizing spending, flagging anomalies, and surfacing decisions you'd otherwise have to make manually every month.

The Problem

Most people know they should track spending and cash flow, but manually categorizing transactions, spotting unusual charges, and adjusting a budget every month is tedious enough that almost nobody keeps it up. The result: financial decisions get made on gut feeling instead of actual data, and problems (a forgotten subscription, an overspending category, a cash flow crunch) get caught late — if at all.

What FinPilot Does

Rather than just visualizing transactions after a human categorizes them, FinPilot acts as an agent in the loop:

Ingests raw bank/credit card CSV exports (up to 200MB per file).
Reasons over each transaction using the Claude API — categorizing it, detecting duplicates/anomalies, and identifying patterns a static rules engine would miss (e.g. a merchant name it hasn't seen before, or a recurring charge that just changed price).
Decides and acts — for example: auto-tagging a transaction with high confidence, flagging low-confidence or unusual transactions for review, and generating a plain-language summary of what changed since the last upload.
Reports via a live dashboard: category breakdown, daily cash flow, and month-over-month comparisons.

Update this section with the exact autonomous actions FinPilot takes in your implementation (e.g. auto-alerts, budget rebalancing suggestions, scheduled digest generation) — keep it concrete and specific to what judges will actually see it do.

Agent Architecture
CSV Upload → Parser → Claude API (categorize / reason / decide) → Action Layer → Dashboard
                                        ↑                              ↓
                                  Transaction history          Alerts / Summaries
Perception: parses uploaded CSV into structured transaction records.
Reasoning: Claude API classifies each transaction and reasons about context (recurring charges, anomalies, category drift).
Action: the agent decides what to surface — auto-categorized entries, flagged items needing review, and generated insights — without needing a human to manually tag every row.
Feedback loop: (if applicable) user corrections feed back into future categorization decisions.
Tech Stack
Backend: Python
AI: Claude API (Anthropic) for transaction reasoning and categorization
Data ingestion: CSV parsing (pandas)
Frontend/Dashboard: (fill in — e.g. Flask templates, React, Streamlit)
Visualization: (fill in — e.g. Chart.js, Plotly)
How to Run
bash
# Clone the repo
git clone https://github.com/<your-username>/finpilot-ai-agent.git
cd finpilot-ai-agent

# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here

# Run the app
python app.py

Open your browser at http://127.0.0.1:5000 and upload a bank/credit card CSV (or use "Load Sample Data" to try it instantly).

Hackathon Info

Built for the Agentic AI Hackathon, organized by Product Space.

Team: Synapse Squad
Project: FinPilot

Note: FinPilot analyzes and acts on financial data but does not move money or connect directly to bank accounts — all actions are informational/advisory unless explicitly stated otherwise in your implementation.

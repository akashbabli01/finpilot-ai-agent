import os
import json
from dotenv import load_dotenv
import anthropic

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL", "claude-3-5-sonnet-20241022")

def get_client() -> anthropic.Anthropic | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.strip() == "" or api_key == "your_anthropic_api_key_here":
        return None
    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}")
        return None

def call_llm_chat(messages: list, tools: list = None, system_prompt: str = None) -> anthropic.types.Message | None:
    """
    Sends messages and optional tool definitions to Anthropic API.
    Returns the Message response object or None if client is unavailable.
    """
    client = get_client()
    if not client:
        return None

    model = os.getenv("MODEL", DEFAULT_MODEL)
    kwargs = {
        "model": model,
        "max_tokens": 4096,
        "messages": messages,
    }
    if system_prompt:
        kwargs["system"] = system_prompt
    if tools:
        kwargs["tools"] = tools

    try:
        response = client.messages.create(**kwargs)
        return response
    except Exception as e:
        print(f"Anthropic API call failed: {e}")
        return None

def categorize_merchants_batched_llm(merchants: list[str]) -> dict | None:
    """
    Batched LLM categorization call for unique merchant descriptions.
    Returns a dict mapping merchant description -> category name, or None if unavailable.
    """
    client = get_client()
    if not client or not merchants:
        return None

    valid_categories = [
        "Rent", "Groceries", "Dining", "Transport", "Subscriptions",
        "Utilities", "Shopping", "Health", "Entertainment", "Income", "Other"
    ]

    prompt = f"""
You are a financial transaction categorizer. Categorize each merchant/description into EXACTLY ONE of these categories:
{valid_categories}

Respond ONLY with a valid JSON object mapping each description to its category name. Do not include markdown code block formatting or extra commentary.

Merchants to categorize:
{json.dumps(merchants, indent=2)}
"""

    model = os.getenv("MODEL", DEFAULT_MODEL)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        # Clean possible markdown block
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
        result = json.loads(text)
        return result
    except Exception as e:
        print(f"LLM batched categorization error: {e}")
        return None

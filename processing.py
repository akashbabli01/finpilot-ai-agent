import pandas as pd
import numpy as np

def normalize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts a raw DataFrame loaded from CSV with varying column names.
    Normalizes columns to: ['date', 'description', 'amount', 'type'].
    Parses dates, handles signed amounts and missing types, and drops bad rows.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=['date', 'description', 'amount', 'type'])

    # Make a copy to avoid mutating original
    clean_df = df.copy()

    # Map headers to lower snake_case string for matching
    col_map = {}
    for col in clean_df.columns:
        c_str = str(col).strip().lower()
        if any(k in c_str for k in ['date', 'time', 'dt', 'txn_date', 'transaction date']):
            col_map[col] = 'date'
        elif any(k in c_str for k in ['desc', 'detail', 'narration', 'merchant', 'particular', 'memo', 'item']):
            col_map[col] = 'description'
        elif any(k in c_str for k in ['amount', 'amt', 'val', 'value', 'price', 'sum']):
            col_map[col] = 'amount'
        elif any(k in c_str for k in ['type', 'dr/cr', 'cr/dr', 'transaction type', 'mode']):
            col_map[col] = 'type'

    clean_df = clean_df.rename(columns=col_map)

    # Required columns verify
    required = ['date', 'description', 'amount']
    missing = [col for col in required if col not in clean_df.columns]
    if missing:
        raise ValueError(f"CSV is missing required financial fields: {missing}. Found columns: {list(clean_df.columns)}")

    # Drop rows where essential fields are NA
    clean_df = clean_df.dropna(subset=['date', 'description', 'amount']).copy()

    # Normalize description
    clean_df['description'] = clean_df['description'].astype(str).str.strip()

    # Normalize amount & type
    # Convert amount to numeric float
    clean_df['amount'] = pd.to_numeric(clean_df['amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
    clean_df = clean_df.dropna(subset=['amount']).copy()

    # Handle type column if missing or sign-based amounts
    if 'type' not in clean_df.columns:
        clean_df['type'] = clean_df['amount'].apply(lambda x: 'credit' if x < 0 else 'debit')
        clean_df['amount'] = clean_df['amount'].abs()
    else:
        # Standardize type string
        def parse_type(row):
            t_val = str(row['type']).strip().lower()
            amt = row['amount']
            if any(k in t_val for k in ['cr', 'credit', 'income', 'deposit', 'received']):
                return 'credit'
            elif any(k in t_val for k in ['dr', 'debit', 'expense', 'spent', 'paid', 'withdrawal']):
                return 'debit'
            else:
                return 'credit' if amt < 0 else 'debit'

        clean_df['type'] = clean_df.apply(parse_type, axis=1)
        clean_df['amount'] = clean_df['amount'].abs()

    # Normalize dates
    clean_df['date'] = pd.to_datetime(clean_df['date'], errors='coerce')
    clean_df = clean_df.dropna(subset=['date']).copy()
    clean_df['date'] = clean_df['date'].dt.strftime('%Y-%m-%d')

    # Sort chronologically
    clean_df = clean_df.sort_values(by='date').reset_index(drop=True)
    return clean_df

def load_and_process_csv(file_path_or_buffer) -> pd.DataFrame:
    """
    Reads CSV file path or file-like buffer, processes and normalizes transactions.
    """
    try:
        df = pd.read_csv(file_path_or_buffer)
        return normalize_transactions(df)
    except Exception as e:
        raise ValueError(f"Failed to process CSV file: {str(e)}")

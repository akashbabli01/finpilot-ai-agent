import os
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_sample_data(filename="sample_transactions.csv"):
    """
    Generates ~600 realistic transaction records over 6 consecutive months (April to September 2026).
    Amounts in INR (₹).
    Columns: date, description, amount, type (debit/credit)
    """
    random.seed(42)  # For reproducible realistic data
    records = []

    # 6 Months: 2026-04 to 2026-09
    months = [
        datetime(2026, 4, 1),
        datetime(2026, 5, 1),
        datetime(2026, 6, 1),
        datetime(2026, 7, 1),
        datetime(2026, 8, 1),
        datetime(2026, 9, 1)
    ]

    for m_idx, m_start in enumerate(months):
        is_latest_month = (m_idx == 5)
        
        # 1. Salary Credit (1st of month)
        salary_date = m_start + timedelta(days=0)
        records.append({
            "date": salary_date.strftime("%Y-%m-%d"),
            "description": "Salary Credit - TechCorp Solutions",
            "amount": 125000.0,
            "type": "credit"
        })
        
        # Freelance Income (Occasional)
        if m_idx in [0, 2, 4, 5]:
            records.append({
                "date": (m_start + timedelta(days=14)).strftime("%Y-%m-%d"),
                "description": "Client Payout - Upwork Escrow",
                "amount": float(random.choice([22000, 28000, 35000, 42000])),
                "type": "credit"
            })

        # 2. Fixed Rent (5th of month)
        records.append({
            "date": (m_start + timedelta(days=4)).strftime("%Y-%m-%d"),
            "description": "HDFC Bank Rent Auto-Debit",
            "amount": 35000.0,
            "type": "debit"
        })

        # 3. Subscriptions (Fixed dates & recurring amounts)
        records.append({"date": (m_start + timedelta(days=7)).strftime("%Y-%m-%d"), "description": "Netflix Subscription", "amount": 649.0, "type": "debit"})
        records.append({"date": (m_start + timedelta(days=11)).strftime("%Y-%m-%d"), "description": "Spotify Premium AutoPay", "amount": 119.0, "type": "debit"})
        records.append({"date": (m_start + timedelta(days=14)).strftime("%Y-%m-%d"), "description": "Cult.fit Gym Membership", "amount": 1750.0, "type": "debit"})
        records.append({"date": (m_start + timedelta(days=19)).strftime("%Y-%m-%d"), "description": "Google One Storage", "amount": 210.0, "type": "debit"})

        # 4. Utilities (Electricity & Wi-Fi around 10th-18th)
        records.append({
            "date": (m_start + timedelta(days=9)).strftime("%Y-%m-%d"),
            "description": "BESCOM Electricity Bill",
            "amount": float(random.randint(2200, 3100)),
            "type": "debit"
        })
        records.append({
            "date": (m_start + timedelta(days=16)).strftime("%Y-%m-%d"),
            "description": "Airtel Xstream Broadband",
            "amount": 1179.0,
            "type": "debit"
        })

        # 5. Groceries (Frequent, ~15 times per month)
        grocery_merchants = ["Blinkit Grocery", "Instamart Mart", "Zepto Supermarket", "BigBasket Order", "Nature's Basket"]
        for day in range(1, 29, 2):
            g_date = m_start + timedelta(days=day + random.randint(0, 1))
            g_date = min(g_date, m_start + timedelta(days=27))
            records.append({
                "date": g_date.strftime("%Y-%m-%d"),
                "description": random.choice(grocery_merchants),
                "amount": float(random.randint(900, 3200)),
                "type": "debit"
            })

        # 6. Dining Out & Food Delivery (Increased trend in recent months)
        dining_count = 12 if m_idx < 3 else (16 if m_idx < 5 else 26)
        dining_merchants = ["Swiggy Order", "Zomato Restaurant", "Starbucks Coffee", "Third Wave Coffee", "Social Bar & Kitchen", "Blue Tokai Coffee"]
        for _ in range(dining_count):
            d_date = m_start + timedelta(days=random.randint(1, 27))
            d_amount = float(random.randint(400, 1100)) if not is_latest_month else float(random.randint(650, 1800))
            records.append({
                "date": d_date.strftime("%Y-%m-%d"),
                "description": random.choice(dining_merchants),
                "amount": d_amount,
                "type": "debit"
            })

        # 7. Transport (Uber, Ola, Fuel, Metro)
        transport_merchants = ["Uber Ride", "Ola Cabs", "Shell Fuel Station", "Namma Metro Recharge"]
        for _ in range(12):
            t_date = m_start + timedelta(days=random.randint(1, 27))
            records.append({
                "date": t_date.strftime("%Y-%m-%d"),
                "description": random.choice(transport_merchants),
                "amount": float(random.randint(250, 1500)),
                "type": "debit"
            })

        # 8. Shopping & Miscellaneous
        shopping_merchants = ["Amazon India", "Myntra Fashion", "Decathlon Sports", "Uniqlo Store", "Zara Clothing"]
        for _ in range(6):
            s_date = m_start + timedelta(days=random.randint(1, 27))
            records.append({
                "date": s_date.strftime("%Y-%m-%d"),
                "description": random.choice(shopping_merchants),
                "amount": float(random.randint(1500, 5200)),
                "type": "debit"
            })

        # Planted Anomaly Spike in Month 6 (September 2026 - Shopping category)
        if is_latest_month:
            records.append({
                "date": (m_start + timedelta(days=17)).strftime("%Y-%m-%d"),
                "description": "Croma Electronics Appliance Purchase",
                "amount": 58500.0,
                "type": "debit"
            })

        # Health & Pharmacy
        for _ in range(3):
            h_date = m_start + timedelta(days=random.randint(2, 26))
            records.append({
                "date": h_date.strftime("%Y-%m-%d"),
                "description": random.choice(["Apollo Pharmacy", "1mg Medicines", "Practo Consultation", "Max Healthcare"]),
                "amount": float(random.randint(500, 2400)),
                "type": "debit"
            })

    # Convert to DataFrame, sort chronologically
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date").reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    filepath = os.path.join(os.path.dirname(__file__), filename)
    df.to_csv(filepath, index=False)
    print(f"Generated {len(df)} transactions over 6 months in '{filepath}'.")
    return df

if __name__ == "__main__":
    generate_sample_data()

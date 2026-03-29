import pandas as pd
import os

def load_income():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "income.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    df["amount"] = pd.to_numeric(df["amount"])
    return df

def monthly_income():
    df = load_income()
    return df.groupby("month")["amount"].sum().reset_index()

def income_by_source():
    df = load_income()
    return df.groupby("source")["amount"].sum()\
             .sort_values(ascending=False)

def total_income():
    df = load_income()
    return df["amount"].sum()

if __name__ == "__main__":
    print("=== Monthly Income ===")
    print(monthly_income())
    print("\n=== Income by Source ===")
    print(income_by_source())
    print("\n=== Total Income ===")
    print(f"₹{total_income():,.0f}")
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Expenses import load_expenses
from income import load_income


def get_base():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_budget():
    path = os.path.join(get_base(), "data", "budget.csv")
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"planned_amount": "monthly_limit"})
    return df


def budget_vs_actual(month):
    budget = load_budget()
    expenses = load_expenses()

    actuals = expenses[expenses["month"] == month]\
              .groupby("category")["amount"].sum()\
              .reset_index()\
              .rename(columns={"amount": "actual"})

    result = budget.merge(actuals, on="category", how="left").fillna(0)
    result["variance"] = result["monthly_limit"] - result["actual"]
    result["pct_used"] = (result["actual"] / result["monthly_limit"] * 100).round(1)
    result["status"] = result["pct_used"].apply(lambda x:
        "OVER BUDGET" if x >= 100 else
        "WARNING"     if x >= 80  else
        "ON TRACK"    if x >= 50  else "UNDER"
    )
    return result.sort_values("pct_used", ascending=False)


def savings_rate(month):
    income   = load_income()
    expenses = load_expenses()

    total_in  = income[income["month"] == month]["amount"].sum()
    total_out = expenses[expenses["month"] == month]["amount"].sum()
    net       = total_in - total_out
    rate      = round((net / total_in) * 100, 1) if total_in > 0 else 0

    return {
        "month":       month,
        "income":      total_in,
        "expenses":    total_out,
        "net_savings": net,
        "savings_rate": f"{rate}%"
    }


if __name__ == "__main__":
    MONTH = "2024-07"
    print("=== Budget vs Actual ===")
    print(budget_vs_actual(MONTH).to_string(index=False))
    print("\n=== Savings Rate ===")
    for k, v in savings_rate(MONTH).items():
        print(f"  {k}: {v}")
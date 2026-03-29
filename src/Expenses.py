import pandas as pd

def load_expenses():
    df = pd.read_csv("data/expenses.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    df["amount"] = pd.to_numeric(df["amount"])
    return df

def monthly_total():
    df = load_expenses()
    return df.groupby("month")["amount"].sum().reset_index()

def top_categories(top_n=5):
    df = load_expenses()
    return df.groupby("category")["amount"].sum()\
             .sort_values(ascending=False)\
             .head(top_n)

def by_type():
    df = load_expenses()
    return df.groupby("type")["amount"].sum()

if __name__ == "__main__":
    print(monthly_total())
    print(top_categories())
    print(by_type())
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from Expenses import load_expenses
from income import load_income
from budget import budget_vs_actual, savings_rate

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Finance Tracker")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["➕ Add Transaction", "📊 Dashboard", "📋 View All"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Add Transaction Form
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Add New Transaction")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💸 Add Expense")
        with st.form("expense_form"):
            exp_date     = st.date_input("Date", value=date.today())
            exp_amount   = st.number_input("Amount (₹)", min_value=1.0, step=100.0)
            exp_category = st.selectbox("Category", [
                "Rent", "EMI", "Groceries", "Utilities", "Transport",
                "Dining Out", "Entertainment", "Shopping", "Healthcare",
                "Subscriptions", "Personal Care", "Education",
                "Credit Card", "Miscellaneous", "Other"
            ])
            exp_type = st.selectbox("Type", ["Fixed", "Variable", "Discretionary"])
            exp_note = st.text_input("Note (optional)", placeholder="e.g. Weekly groceries")
            submit_expense = st.form_submit_button("Add Expense ➕")

            if submit_expense:
                if exp_amount <= 0:
                    st.error("Amount must be greater than 0!")
                else:
                    base = os.path.dirname(os.path.abspath(__file__))
                    path = os.path.join(base, "data", "expenses.csv")
                    df   = pd.read_csv(path)
                    new_row = pd.DataFrame([{
                        "date":     str(exp_date),
                        "amount":   exp_amount,
                        "category": exp_category,
                        "type":     exp_type,
                        "note":     exp_note
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(path, index=False)
                    st.success(f"✅ Expense of ₹{exp_amount:,.0f} added under {exp_category}!")

    with col2:
        st.markdown("#### 💰 Add Income")
        with st.form("income_form"):
            inc_date   = st.date_input("Date", value=date.today(), key="inc_date")
            inc_amount = st.number_input("Amount (₹)", min_value=1.0, step=1000.0, key="inc_amt")
            inc_source = st.selectbox("Source", [
                "Salary", "Freelance", "Dividend",
                "Rental", "Business", "Other"
            ])
            inc_note = st.text_input("Note (optional)", placeholder="e.g. July salary", key="inc_note")
            submit_income = st.form_submit_button("Add Income ➕")

            if submit_income:
                if inc_amount <= 0:
                    st.error("Amount must be greater than 0!")
                else:
                    base = os.path.dirname(os.path.abspath(__file__))
                    path = os.path.join(base, "data", "income.csv")
                    df   = pd.read_csv(path)
                    new_row = pd.DataFrame([{
                        "date":   str(inc_date),
                        "amount": inc_amount,
                        "source": inc_source,
                        "note":   inc_note
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(path, index=False)
                    st.success(f"✅ Income of ₹{inc_amount:,.0f} from {inc_source} added!")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    expenses = load_expenses()
    income   = load_income()

    months = sorted(expenses["month"].astype(str).unique(), reverse=True)
    selected_month = st.selectbox("Select Month", months)

    # Summary metrics
    summary = savings_rate(selected_month)
    st.subheader(f"Summary – {selected_month}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income",   f"₹{summary['income']:,.0f}")
    col2.metric("Total Expenses", f"₹{summary['expenses']:,.0f}")
    col3.metric("Net Savings",    f"₹{summary['net_savings']:,.0f}")
    col4.metric("Savings Rate",   summary["savings_rate"])

    st.divider()

    # Charts
    col_left, col_right = st.columns(2)
    month_expenses = expenses[expenses["month"] == selected_month]

    with col_left:
        st.subheader("Spending by Category")
        cat_data = month_expenses.groupby("category")["amount"].sum().reset_index()
        fig1 = px.pie(cat_data, values="amount", names="category", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Spending by Type")
        type_data = month_expenses.groupby("type")["amount"].sum().reset_index()
        fig2 = px.bar(type_data, x="type", y="amount", color="type",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Budget vs Actual
    st.subheader("Budget vs Actual")
    budget_data = budget_vs_actual(selected_month)
    fig3 = px.bar(budget_data, x="category", y=["monthly_limit", "actual"],
                  barmode="group",
                  color_discrete_map={"monthly_limit": "#636EFA", "actual": "#EF553B"},
                  labels={"value": "Amount (₹)", "variable": "Type"})
    st.plotly_chart(fig3, use_container_width=True)

    # Budget status table
    st.subheader("Budget Status")
    st.dataframe(budget_data.style.applymap(
        lambda x: "background-color: #ffcccc" if x == "OVER BUDGET"
             else "background-color: #fff3cc" if x == "WARNING"
             else "",
        subset=["status"]
    ), use_container_width=True)

    st.divider()

    # Monthly trend
    st.subheader("Monthly Trend – Income vs Expenses")
    inc_monthly = income.groupby("month")["amount"].sum().reset_index().rename(columns={"amount": "income"})
    exp_monthly = expenses.groupby("month")["amount"].sum().reset_index().rename(columns={"amount": "expenses"})
    trend = inc_monthly.merge(exp_monthly, on="month")
    trend["month"] = trend["month"].astype(str)
    fig4 = px.line(trend, x="month", y=["income", "expenses"], markers=True,
                   color_discrete_map={"income": "#00CC96", "expenses": "#EF553B"})
    st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — View All Transactions
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("All Expenses")
    expenses_all = load_expenses()

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        cat_filter = st.multiselect("Filter by Category",
                                     options=expenses_all["category"].unique())
    with col2:
        type_filter = st.multiselect("Filter by Type",
                                      options=expenses_all["type"].unique())

    filtered = expenses_all.copy()
    if cat_filter:
        filtered = filtered[filtered["category"].isin(cat_filter)]
    if type_filter:
        filtered = filtered[filtered["type"].isin(type_filter)]

    st.dataframe(filtered.drop(columns=["month"]).sort_values("date", ascending=False),
                 use_container_width=True)

    st.divider()

    st.subheader("All Income")
    st.dataframe(load_income().drop(columns=["month"]).sort_values("date", ascending=False),
                 use_container_width=True)
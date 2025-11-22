# app.py
import streamlit as st
import pandas as pd
from datetime import date

from database import (
    init_db,
    add_transaction,
    get_all_transactions,
    get_summary,
    set_goal,
    get_goal_progress,
    get_goal,
)

# Initialize database
init_db()

st.set_page_config(page_title="Smart Personal Expense Tracker", layout="centered")

# --- HEADER ---
st.title("💰 Smart Personal Expense Tracker")

username = st.text_input("Enter your name (no password required):", value="User")
if username.strip() == "":
    username = "User"

st.caption(f"Welcome, **{username}**! Track your expenses and goals below.")


# --- SIDEBAR NAVIGATION ---
page = st.sidebar.radio(
    "Navigate",
    ["Balance & Goals", "Add Transaction", "History & Summary"],
)


# --- PAGE 1: Balance & Goals ---
if page == "Balance & Goals":
    st.header("📊 Balance & Spending Goals")

    total_income, total_expense, balance = get_summary()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹ {total_income:.2f}")
    col2.metric("Total Expense", f"₹ {total_expense:.2f}")
    col3.metric("Current Balance", f"₹ {balance:.2f}")

    st.subheader("Set / Update Goals")

    colg1, colg2 = st.columns(2)

    with colg1:
        monthly_goal = st.number_input(
            "Monthly spending limit (₹)", min_value=0.0, step=500.0, value=float(get_goal("monthly") or 0.0)
        )
        if st.button("Save Monthly Goal"):
            set_goal("monthly", monthly_goal)
            st.success("Monthly goal saved successfully!")

    with colg2:
        weekly_goal = st.number_input(
            "Weekly spending limit (₹)", min_value=0.0, step=200.0, value=float(get_goal("weekly") or 0.0)
        )
        if st.button("Save Weekly Goal"):
            set_goal("weekly", weekly_goal)
            st.success("Weekly goal saved successfully!")

    st.markdown("---")
    st.subheader("Goal Status")

    for g_type, label in [("monthly", "Monthly"), ("weekly", "Weekly")]:
        goal_amount, spent, remaining, status = get_goal_progress(g_type)
        st.markdown(f"### {label} Goal")
        if goal_amount is None:
            st.info(f"No {label.lower()} goal set yet.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Goal Amount", f"₹ {goal_amount:.2f}")
            c2.metric("Spent so far", f"₹ {spent:.2f}")
            c3.metric("Remaining", f"₹ {remaining:.2f}")
            if "exceeded" in status:
                st.error(status)
            elif "close" in status:
                st.warning(status)
            else:
                st.success(status)


# --- PAGE 2: Add Transaction ---
elif page == "Add Transaction":
    st.header("➕ Add Expense or Received Money")

    t_type = st.radio("Transaction type:", ["Expense", "Income (Received Money)"])
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    category = st.text_input("Category (e.g., Food, Travel, Fees, Salary)", value="")
    t_date = st.date_input("Date", value=date.today())
    note = st.text_area("Note (optional)", height=60)

    if st.button("Add Transaction"):
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        elif category.strip() == "":
            st.error("Please enter a category.")
        else:
            db_type = "expense" if t_type.startswith("Expense") else "income"
            add_transaction(
                t_type=db_type,
                amount=amount,
                category=category.strip(),
                t_date=t_date.isoformat(),
                note=note.strip(),
            )
            if db_type == "expense":
                st.success("Expense added and balance updated.")
            else:
                st.success("Income added and balance updated.")


# --- PAGE 3: History & Summary ---
elif page == "History & Summary":
    st.header("📜 Transaction History & Summary")

    rows = get_all_transactions()
    if not rows:
        st.info("No transactions recorded yet.")
    else:
        df = pd.DataFrame(
            rows, columns=["ID", "Date", "Type", "Category", "Amount", "Note"]
        )
        # Convert to proper types
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

        st.subheader("All Transactions")
        st.dataframe(df, height=400)

        total_income, total_expense, balance = get_summary()
        st.markdown("---")
        st.subheader("Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"₹ {total_income:.2f}")
        col2.metric("Total Expense", f"₹ {total_expense:.2f}")
        col3.metric("Current Balance", f"₹ {balance:.2f}")

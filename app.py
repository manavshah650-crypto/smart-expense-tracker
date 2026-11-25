

import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    add_transaction,
    get_transactions,
    delete_transaction,
    update_transaction,
    save_budget,
    get_budget,
    get_monthly_expenses
)

from smart_features import categorize_expense, generate_insights

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Smart Expense Tracker")
st.caption("Manage your income, expenses and monthly budget in one place.")

# Sidebar navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Transaction", "Manage Transactions",
     "Budget Manager", "Smart Insights"]
)

# DASHBOARD
if menu == "Dashboard":

    st.header("📊 Financial Dashboard")

    df = get_transactions()

    if df.empty:
        st.info("No transactions yet. Start by adding a transaction.")
    else:
        income = df[df["transaction_type"] == "Income"]["amount"].sum()
        expenses = df[df["transaction_type"] == "Expense"]["amount"].sum()
        balance = income - expenses

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Income", f"₹{income:,.2f}")
        col2.metric("Total Expenses", f"₹{expenses:,.2f}")
        col3.metric("Current Balance", f"₹{balance:,.2f}")

        st.subheader("Transaction History")
        st.dataframe(df, use_container_width=True)

        expense_df = df[df["transaction_type"] == "Expense"]

        if not expense_df.empty:
            st.subheader("Expenses by Category")

            category_data = expense_df.groupby(
                "category", as_index=False
            )["amount"].sum()

            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                title="Category-wise Spending",
                hole=0.4
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Monthly Expense Overview")

            monthly_data = expense_df.copy()
            monthly_data["month"] = pd.to_datetime(
                monthly_data["date"]
            ).dt.to_period("M").astype(str)

            monthly_data = monthly_data.groupby(
                "month", as_index=False
            )["amount"].sum()

            fig2 = px.bar(
                monthly_data,
                x="month",
                y="amount",
                title="Monthly Expenses",
                labels={"amount": "Expense (₹)", "month": "Month"}
            )

            st.plotly_chart(fig2, use_container_width=True)


# ADD TRANSACTION
elif menu == "Add Transaction":

    st.header("➕ Add New Transaction")

    with st.form("transaction_form"):

        title = st.text_input("Transaction Description")

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        transaction_type = st.selectbox(
            "Transaction Type",
            ["Expense", "Income"]
        )

        category_options = [
            "Auto", "Food", "Travel", "Shopping",
            "Utilities", "Entertainment", "Salary",
            "Business", "Other"
        ]

        category = st.selectbox("Category", category_options)

        transaction_date = st.date_input("Transaction Date")

        submitted = st.form_submit_button("Save Transaction")

        if submitted:

            if not title.strip():
                st.error("Please enter a transaction description.")

            elif amount <= 0:
                st.error("Amount must be greater than zero.")

            else:

                if category == "Auto" and transaction_type == "Expense":
                    category = categorize_expense(title)

                elif category == "Auto":
                    category = "Other"

                add_transaction(
                    title,
                    amount,
                    category,
                    transaction_type,
                    transaction_date
                )

                st.success("Transaction added successfully!")
                st.rerun()


# MANAGE TRANSACTIONS
elif menu == "Manage Transactions":

    st.header("📝 Manage Transactions")

    df = get_transactions()

    if df.empty:
        st.info("No transactions available.")
    else:

        st.dataframe(df, use_container_width=True)

        transaction_id = st.selectbox(
            "Select Transaction ID",
            df["id"].tolist()
        )

        selected = df[df["id"] == transaction_id].iloc[0]

        st.subheader("Edit Selected Transaction")

        with st.form("edit_form"):

            new_title = st.text_input(
                "Description",
                value=str(selected["title"])
            )

            new_amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=float(selected["amount"])
            )

            new_type = st.selectbox(
                "Type",
                ["Expense", "Income"],
                index=["Expense", "Income"].index(
                    selected["transaction_type"]
                )
            )

            categories = [
                "Food", "Travel", "Shopping", "Utilities",
                "Entertainment", "Salary", "Business", "Other"
            ]

            old_category = selected["category"]

            category_index = (
                categories.index(old_category)
                if old_category in categories else categories.index("Other")
            )

            new_category = st.selectbox(
                "Category",
                categories,
                index=category_index
            )

            new_date = st.date_input(
                "Date",
                value=pd.to_datetime(selected["date"]).date()
            )

            update_button = st.form_submit_button("Update Transaction")

            if update_button:

                if not new_title.strip():
                    st.error("Description cannot be empty.")

                else:
                    update_transaction(
                        transaction_id,
                        new_title,
                        new_amount,
                        new_category,
                        new_type,
                        new_date
                    )

                    st.success("Transaction updated!")
                    st.rerun()

        if st.button("🗑️ Delete Selected Transaction"):
            delete_transaction(transaction_id)
            st.success("Transaction deleted!")
            st.rerun()


# BUDGET MANAGER
elif menu == "Budget Manager":

    st.header("💳 Monthly Budget Manager")

    month = st.text_input(
        "Enter Month (YYYY-MM)",
        value=pd.Timestamp.today().strftime("%Y-%m")
    )

    if len(month) == 7:

        budget = st.number_input(
            "Set Monthly Budget (₹)",
            min_value=0.0,
            step=500.0
        )

        if st.button("Save Budget"):
            if budget > 0:
                save_budget(month, budget)
                st.success("Budget saved successfully!")
            else:
                st.error("Budget must be greater than zero.")

        saved_budget = get_budget(month)
        monthly_expense = get_monthly_expenses(month)

        if saved_budget > 0:

            st.metric("Monthly Budget", f"₹{saved_budget:,.2f}")
            st.metric("Amount Spent", f"₹{monthly_expense:,.2f}")

            remaining = saved_budget - monthly_expense

            st.metric("Remaining Budget", f"₹{remaining:,.2f}")

            progress = min(monthly_expense / saved_budget, 1.0)

            st.progress(progress)

            if monthly_expense >= saved_budget:
                st.error("You have exceeded your monthly budget!")

            elif monthly_expense >= saved_budget * 0.8:
                st.warning("Warning: You have used 80% of your budget.")

            else:
                st.success("You are within your budget.")

        else:
            st.info("Set and save a budget to track your monthly spending.")

    else:
        st.error("Please enter month in YYYY-MM format.")


# SMART INSIGHTS
elif menu == "Smart Insights":

    st.header("🧠 Smart Spending Insights")

    df = get_transactions()

    insights = generate_insights(df)

    for insight in insights:
        st.info(insight)

    if not df.empty:

        expenses = df[df["transaction_type"] == "Expense"]

        if not expenses.empty:

            category_totals = expenses.groupby(
                "category"
            )["amount"].sum()

            st.subheader("Spending Analysis")

            st.bar_chart(category_totals)


st.sidebar.divider()
st.sidebar.caption("Smart Expense Tracker | Built with Python and Streamlit")


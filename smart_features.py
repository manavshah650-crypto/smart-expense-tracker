

import pandas as pd


def categorize_expense(title):
    title = title.lower()

    categories = {
        "Food": ["pizza", "restaurant", "grocery", "food",
                 "burger", "swiggy", "zomato"],
        "Travel": ["uber", "ola", "taxi", "bus", "train",
                   "flight", "petrol"],
        "Shopping": ["amazon", "clothes", "shopping",
                     "flipkart", "shoes"],
        "Utilities": ["electricity", "water", "internet",
                      "mobile", "bill"],
        "Entertainment": ["movie", "netflix", "game",
                          "concert"]
    }

    for category, keywords in categories.items():
        if any(word in title for word in keywords):
            return category

    return "Other"


def generate_insights(df):
    insights = []

    if df.empty:
        return ["Add transactions to generate insights."]

    expenses = df[df["transaction_type"] == "Expense"]

    if expenses.empty:
        return ["No expenses recorded yet."]

    category_totals = expenses.groupby("category")["amount"].sum()

    highest_category = category_totals.idxmax()
    highest_amount = category_totals.max()

    insights.append(
        f"Your highest spending category is {highest_category} "
        f"(₹{highest_amount:,.2f})."
    )

    total_expense = expenses["amount"].sum()
    insights.append(
        f"Your total recorded expenses are ₹{total_expense:,.2f}."
    )

    average_expense = expenses["amount"].mean()
    insights.append(
        f"Your average transaction amount is ₹{average_expense:,.2f}."
    )

    return insights

import pandas as pd
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def load_transactions(user_id):
    conn = get_connection()
    query = """
        SELECT
            t.transaction_id,
            t.category_id,
            c.category_name,
            c.category_type,
            t.amount,
            t.type,
            t.transaction_date,
            t.description,
            t.created_at
        FROM `Transaction` t
        JOIN category c ON t.category_id = c.category_id
        WHERE c.user_id = %s
        ORDER BY t.transaction_date ASC
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    df["amount"] = df["amount"].astype(float)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


def load_categories(user_id):
    conn = get_connection()
    query = """
        SELECT category_id, category_name, category_type, budget
        FROM category
        WHERE user_id = %s AND is_active = TRUE
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce")
    return df


def summary(df):
    total_income = df[df["category_type"] == "income"]["amount"].sum()
    total_spending = df[df["category_type"] == "spending"]["amount"].sum()
    return {
        "total_income": round(total_income, 2),
        "total_spending": round(total_spending, 2),
        "num_transactions": len(df),
    }


def spending_by_category(df):
    spending_df = df[df["category_type"] == "spending"]
    grouped = spending_df.groupby("category_name")["amount"].sum().reset_index()
    grouped.columns = ["category_name", "total_spent"]
    return grouped.sort_values("total_spent", ascending=False).round(2)


def income_by_category(df):
    income_df = df[df["category_type"] == "income"]
    grouped = income_df.groupby("category_name")["amount"].sum().reset_index()
    grouped.columns = ["category_name", "total_income"]
    return grouped.sort_values("total_income", ascending=False).round(2)


def spending_by_month(df):
    df = df.copy()
    df["month"] = df["transaction_date"].dt.to_period("M")
    spending_df = df[df["category_type"] == "spending"]

    grouped = spending_df.groupby("month")["amount"].sum().reset_index()
    grouped.columns = ["month", "total_spent"]
    grouped["month"] = grouped["month"].astype(str)
    return grouped.round(2)


def income_by_month(df):
    df = df.copy()
    df["month"] = df["transaction_date"].dt.to_period("M")
    income_df = df[df["category_type"] == "income"]

    grouped = income_df.groupby("month")["amount"].sum().reset_index()
    grouped.columns = ["month", "total_income"]
    grouped["month"] = grouped["month"].astype(str)
    return grouped.round(2)


def monthly_overview(df):
    # Merges income and spending by month into one DataFrame for easy comparison
    income = income_by_month(df)
    spending = spending_by_month(df)
    merged = income.merge(spending, on="month", how="outer").fillna(0)
    merged["net_savings"] = (merged["total_income"] - merged["total_spent"]).round(2)
    return merged.sort_values("month").round(2)


def budget_vs_spending(df, categories_df):
    spending_cats = categories_df[categories_df["category_type"] == "spending"]
    spending_df = df[df["category_type"] == "spending"]

    withdrawals = (
        spending_df.groupby("category_name")["amount"]
        .sum()
        .reset_index()
    )
    withdrawals.columns = ["category_name", "total_spent"]

    merged = spending_cats.merge(withdrawals, on="category_name", how="left")
    merged["total_spent"] = merged["total_spent"].fillna(0)
    merged["remaining"] = merged["budget"] - merged["total_spent"]
    merged["usage_%"] = (
        merged["total_spent"] / merged["budget"].replace(0, float("nan")) * 100
    ).round(1)

    return merged.round(2)


def top_spending_categories(df, n=3):
    return (
        df[df["category_type"] == "spending"]
        .groupby("category_name")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
        .rename(columns={"amount": "total_spent"})
        .round(2)
    )


if __name__ == "__main__":
    USER_ID = 1

    df = load_transactions(USER_ID)
    categories_df = load_categories(USER_ID)

    print(f"Loaded {len(df)} transactions\n")

    print("── Summary ──────────────────────────────")
    for k, v in summary(df).items():
        print(f"  {k}: {v}")

    print("\n── Monthly Overview ─────────────────────")
    print(monthly_overview(df).to_string(index=False))

    print("\n── Budget vs Spending ───────────────────")
    print(budget_vs_spending(df, categories_df).to_string(index=False))

    print("\n── Top 3 Spending Categories ────────────")
    print(top_spending_categories(df).to_string(index=False))
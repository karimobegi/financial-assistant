import pandas as pd
import sqlite3
def load_data(path = 'data/finance.db'):
    conn = sqlite3.connect(path)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    conn.close()
    return df
def category_analysis(df):
    expense_df = df[df["category"] != "Income"]
    if expense_df.empty:
        return {
            "total_by_category": None,
            "avg_by_category": None,
            "count_by_category": None,
            "percent_by_category": None,
            "high_share_categories": None,
            "top_spending_category": None,
            "top_spending_value": None,
        }

    cat_group = expense_df.groupby("category")

    total_by_cat = cat_group["abs_amount"].sum()
    avg_by_cat = cat_group["abs_amount"].mean()
    count_by_cat = cat_group.size()
    percent_by_cat = total_by_cat * 100 / total_by_cat.sum()

    high_share_cat = percent_by_cat[percent_by_cat > 20]

    top_cat = total_by_cat.idxmax()
    top_val = float(total_by_cat.loc[top_cat])

    return {
        "total_by_category": total_by_cat,
        "avg_by_category": avg_by_cat,
        "count_by_category": count_by_cat,
        "percent_by_category": percent_by_cat,
        "high_share_categories": high_share_cat,
        "top_spending_category": top_cat,
        "top_spending_value": top_val,
    }
def time_analysis(df):
    expenses = df[df["category"] != "Income"].groupby("month")["abs_amount"]
    total_by_month = expenses.sum()
    highest_month = total_by_month.idxmax()
    highest_value = total_by_month.loc[highest_month]
    has_trend = total_by_month.size >= 2
    month_over_month_change = total_by_month.diff() if has_trend else None
    return {
        "total_by_month": total_by_month,
        "highest_month": highest_month,
        "highest_month_value": highest_value,
        "has_trend": has_trend,
        "month_over_month_change": month_over_month_change,
    }
def outlier_analysis(df):
    expense_df = df[df['category'] != 'Income']
    if expense_df.empty:
        return {
            "mean_amount": 0,
            "large_transactions": expense_df,
            "num_large_transactions": 0,
        }


    mean_amount = expense_df['abs_amount'].mean()
    large_transactions = expense_df[expense_df['abs_amount'] > 2 * mean_amount]

    return {
        "mean_amount": mean_amount,
        "large_transactions": large_transactions,
        "num_large_transactions": len(large_transactions),
    }
def cashflow_analysis(df):
    monthly = df.groupby(['month', 'category'])['amount'].sum().unstack(fill_value=0)
    income = monthly.get('Income', 0)
    expenses = monthly.drop(columns=['Income'], errors='ignore').sum(axis=1)
    net_savings = income + expenses
    total_net = net_savings.sum()
    num_months = net_savings.shape[0]
    last_month_num = int(str(net_savings.index[-1]).split("-")[1])
    remaining_months = max(0, 12 - last_month_num)
    future_expected = (
        total_net * remaining_months / num_months
        if num_months > 0 else 0
    )
    return {
        "income_by_month": income,
        "expenses_by_month": expenses,
        "net_savings_by_month": net_savings,
        "total_net_savings": net_savings.sum(),
        "expectation": future_expected
    }
def run_analysis(path="data/finance.db"):
    df = load_data(path)
    expense_df = df[df['category'] != 'Income']
    results = {
    "cashflow": cashflow_analysis(df),
    "category": category_analysis(df),
    "time": time_analysis(df),
    "outliers": outlier_analysis(df),
    "top_merchants":(
            expense_df.groupby('merchant')['abs_amount']
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )
    }
    return results
if __name__ == "__main__":
    analysis_results = run_analysis()




def category_advice(results):
    advice = []

    cat = results["category"]
    percent_by_category = cat["percent_by_category"]          
    high_share = cat["high_share_categories"]                 
    total_by_category = cat["total_by_category"]              
    
   
    if not high_share.empty:
        #Sort so biggest categories appear first
        high_share_sorted = high_share.sort_values(ascending=False)

        parts = [f"{name} ({pct:.1f}%)" for name, pct in high_share_sorted.items()]
        advice.append("High-spend categories: " + ", ".join(parts) + ".")

    
    top_cat = percent_by_category.idxmax()
    top_pct = float(percent_by_category.loc[top_cat])
    if top_pct > 40:
        advice.append(f"Spending is highly concentrated in {top_cat} ({top_pct:.1f}%).")

    
    top_total_cat = total_by_category.idxmax()
    top_total_val = float(total_by_category.loc[top_total_cat])
    advice.append(f"Top spending category by total: {top_total_cat} ({top_total_val:.2f}).")

    return advice

def outlier_advice(results):
    advice = []

    out = results["outliers"]
    num_large = out["num_large_transactions"]
    large_df = out["large_transactions"]
    mean_amount = float(out["mean_amount"])

    #any large transactions exist
    if num_large > 0:
        advice.append(f"You had {num_large} unusually large transaction(s).")

        #highlight the largest outlier
        largest = float(large_df["abs_amount"].max())

        if largest > 3 * mean_amount:
            largest_row = large_df.loc[
                large_df["abs_amount"] == largest
            ].iloc[0]

            merchant = largest_row["merchant"]
            date = largest_row["date"]
            category = largest_row["category"]
            advice.append(
                f"The largest transaction was {largest:.2f} "
                f"at {merchant} ({category}) on {date}."
            )

    else:
        #no outliers
        advice.append("No unusually large transactions were detected.")

    return advice
def cashflow_advice(results):
    advice = []

    cashflow = results.get("cashflow")
    if not cashflow:
        return advice

    net_by_month = cashflow.get("net_savings_by_month")
    total_net = cashflow.get("total_net_savings")

    if net_by_month is None or net_by_month.empty:
        advice.append("Not enough data to assess savings over time.")
        return advice

    #Overall savings health
    if total_net > 0:
        advice.append(
            f"Overall, you saved money during the analyzed period (+{total_net:.2f})."
        )
    elif total_net < 0:
        advice.append(
            f"Overall, you spent more than you earned during the analyzed period ({total_net:.2f})."
        )
    else:
        advice.append("Overall, your income and expenses balanced out.")

    #Best and worst months
    best_month = net_by_month.idxmax()
    best_value = net_by_month.loc[best_month]

    worst_month = net_by_month.idxmin()
    worst_value = net_by_month.loc[worst_month]

    advice.append(
        f"Your best savings month was {best_month} (+{best_value:.2f})."
    )

    if worst_value < 0:
        advice.append(
            f"You overspent the most in {worst_month} ({worst_value:.2f})."
        )

    #Overspending warning
    negative_months = net_by_month[net_by_month < 0]
    if not negative_months.empty:
        advice.append(
            f"You had {len(negative_months)} month(s) where expenses exceeded income."
        )

    #Month-over-month trend (if possible)
    if len(net_by_month) >= 2:
        last_change = net_by_month.iloc[-1] - net_by_month.iloc[-2]

        if last_change > 0:
            advice.append("Your net savings improved compared to the previous month.")
        elif last_change < 0:
            advice.append("Your net savings declined compared to the previous month.")
        else:
            advice.append("Your net savings remained stable compared to the previous month.")

    #Consistency signal
    if (net_by_month > 0).all():
        advice.append("You consistently saved money every month.")
    elif (net_by_month <= 0).all():
        advice.append("You did not save money in any of the analyzed months.")
    exp = cashflow.get("expectation")
    if exp is not None:
        if exp > 0:
            advice.append(
                f"Based on your current pace, you could save approximately {exp:.2f} over the rest of the year."
            )
        else:
            advice.append(
                f"At your current pace, you may lose around {abs(exp):.2f} over the rest of the year."
            )

    return advice
def trend_advice(results):
    advice = []

    t = results["time"]
    has_trend = t["has_trend"]

    if not has_trend:
        advice.append("Not enough monthly history to assess spending trends.")
        return advice

    mom = t["month_over_month_change"]  
    last_change = float(mom.iloc[-1])

    if last_change > 0:
        advice.append(f"Spending increased compared to the previous month (+{last_change:.2f}).")
    elif last_change < 0:
        advice.append(f"Spending decreased compared to the previous month ({last_change:.2f}).")
    else:
        advice.append("Spending was stable compared to the previous month.")

    return advice
def generate_advice(results):
    advice = []
    advice.extend(category_advice(results))
    advice.extend(outlier_advice(results))
    advice.extend(trend_advice(results))
    advice.extend(cashflow_advice(results))
    return advice

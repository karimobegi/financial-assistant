import csv
from datetime import datetime
def ingest_transactions(
    input_path="data/raw_transactions/payments.csv",
    output_path="data/clean_transactions.csv",
):
    rows_read = 0
    rows_written = 0
    rows_skipped = 0
    skip_reasons = {
        "missing_fields": 0,
        "invalid_amount": 0,
        "invalid_date": 0,
    }

    with open(input_path, "r", newline="", encoding="utf-8") as transactions:
        csv_reader = csv.DictReader(transactions)

        fieldnames = [
            "date",
            "merchant",
            "amount",
            "abs_amount",
            "category",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as clean_t:
            csv_writer = csv.DictWriter(clean_t, fieldnames=fieldnames)
            csv_writer.writeheader()
            for line in csv_reader:
                rows_read += 1
                if not line.get("merchant") or not line.get("amount") or not line.get("date"):
                    rows_skipped += 1
                    skip_reasons["missing_fields"] += 1
                    continue

                merchant = line["merchant"].lower().strip()

                
                try:
                    amount = float(line["amount"].replace(",", ""))
                except ValueError:
                    rows_skipped += 1
                    skip_reasons["invalid_amount"] += 1
                    continue
                try:
                    date = datetime.strptime(line["date"], "%Y-%m-%d").date()
                except ValueError:
                    rows_skipped += 1
                    skip_reasons["invalid_date"] += 1
                    continue
                
                merchant = merchant.lower()

                if any(k in merchant for k in [
                    "uber", "lime", "bolt", "careem", "taxi", "metro", "bus", "train"
                ]):
                    category = "Transport"

                elif any(k in merchant for k in [
                    "netflix", "spotify", "amazon prime", "youtube premium",
                    "apple.com/bill", "google *services", "icloud", "dropbox"
                ]):
                    category = "Subscription"

                elif any(k in merchant for k in [
                    "salary", "payroll", "wage", "income"
                ]):
                    category = "Income"

                elif any(k in merchant for k in [
                    "carrefour", "waitrose", "tesco", "costco",
                    "aldi", "lidl", "supermarket", "grocery"
                ]):
                    category = "Groceries"

                elif any(k in merchant for k in [
                    "zara", "h&m", "hm", "uniqlo", "ikea",
                    "amazon", "shein", "decathlon"
                ]):
                    category = "Shopping"

                elif any(k in merchant for k in [
                    "uber eats", "deliveroo", "talabat",
                    "just eat", "doordash"
                ]):
                    category = "Ordering"

                elif any(k in merchant for k in [
                    "restaurant", "cafe", "coffee", "starbucks",
                    "mcdonald", "kfc", "burger king"
                ]):
                    category = "Restaurants"

                elif any(k in merchant for k in [
                    "electric", "electricity", "water", "internet",
                    "vodafone", "orange", "ooredoo", "etisalat"
                ]):
                    category = "Bills"

                elif any(k in merchant for k in [
                    "pharmacy", "hospital", "clinic", "dentist"
                ]):
                    category = "Health"

                elif any(k in merchant for k in [
                    "atm", "cash withdrawal"
                ]):
                    category = "Cash"

                elif any(k in merchant for k in [
                    "fee", "commission", "bank charge", "interest"
                ]):
                    category = "Bank Fees"

                else:
                    category = "Other"
                csv_writer.writerow(
                    {
                        "date": date.isoformat(),
                        "merchant": merchant,
                        "amount": amount,
                        "abs_amount": abs(amount),
                        "category": category,
                    }
                )

                rows_written += 1

    return {
        "output_path": output_path,
        "rows_read": rows_read,
        "rows_written": rows_written,
        "rows_skipped": rows_skipped,
        "skip_reasons": skip_reasons,
    }
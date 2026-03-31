from src.mongo_client import get_mongo_client
from src.transaction_report import get_customer_transaction_summary, format_customer_summary


def main() -> None:
    client = get_mongo_client()
    db = client.sample_analytics
    summaries = get_customer_transaction_summary(db)

    if not summaries:
        print("No customer summaries were found in sample_analytics.customers.")
        return

    for summary in summaries:
        print(format_customer_summary(summary))
        print("-")


if __name__ == "__main__":
    main()

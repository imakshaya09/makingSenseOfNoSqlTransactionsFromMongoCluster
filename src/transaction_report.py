from typing import Any, Dict, List

from pymongo.database import Database


CUSTOMERS_COLLECTION = "customers"
ACCOUNTS_COLLECTION = "accounts"
TRANSACTIONS_COLLECTION = "transactions"


def build_customer_transaction_summary_pipeline() -> List[Dict[str, Any]]:
    """Build a MongoDB aggregation pipeline that computes transaction sums per customer."""
    return [
        {"$unwind": {"path": "$accounts", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": ACCOUNTS_COLLECTION,
                "localField": "accounts",
                "foreignField": "account_id",
                "as": "account",
            }
        },
        {"$unwind": {"path": "$account", "preserveNullAndEmptyArrays": True}},
        {
            "$lookup": {
                "from": TRANSACTIONS_COLLECTION,
                "localField": "account.account_id",
                "foreignField": "account_id",
                "as": "transaction_docs",
            }
        },
        {
            "$unwind": {
                "path": "$transaction_docs",
                "preserveNullAndEmptyArrays": True,
            }
        },
        {
            "$addFields": {
                "transactionTotal": {
                    "$sum": {
                        "$map": {
                            "input": {"$ifNull": ["$transaction_docs.transactions", []]},
                            "as": "tx",
                            "in": {
                                "$toDouble": {
                                    "$ifNull": ["$$tx.total", "0"]
                                }
                            },
                        }
                    }
                },
                "accountLimit": "$account.limit",
                "accountId": "$account.account_id",
            }
        },
        {
            "$group": {
                "_id": "$name",
                "customerTotal": {"$sum": "$transactionTotal"},
                "accounts": {
                    "$push": {
                        "account_id": "$accountId",
                        "limit": "$accountLimit",
                        "transactionTotal": "$transactionTotal",
                    }
                },
            }
        },
        {
            "$addFields": {
                "exceededAnyAccountLimit": {
                    "$anyElementTrue": {
                        "$map": {
                            "input": {
                                "$filter": {
                                    "input": "$accounts",
                                    "as": "acct",
                                    "cond": {
                                        "$and": [
                                            {"$ne": ["$$acct.account_id", None]},
                                            {"$ne": ["$$acct.limit", None]},
                                        ]
                                    },
                                }
                            },
                            "as": "acct",
                            "in": {"$lt": ["$$acct.limit", "$customerTotal"]},
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "name": "$_id",
                "customerTotal": 1,
                "accounts": 1,
                "exceededAnyAccountLimit": 1,
            }
        },
    ]


def get_customer_transaction_summary(db: Database) -> List[Dict[str, Any]]:
    """Execute the aggregation and return customer transaction summaries."""
    pipeline = build_customer_transaction_summary_pipeline()
    return list(db[CUSTOMERS_COLLECTION].aggregate(pipeline))


def format_customer_summary(summary: Dict[str, Any]) -> str:
    """Render a single customer summary line for output."""
    return (
        f"Customer: {summary.get('name', '<unknown>')}\n"
        f"  Total Transactions: {summary.get('customerTotal', 0)}\n"
        f"  Exceeded Any Account Limit: {summary.get('exceededAnyAccountLimit', False)}\n"
        f"  Accounts:\n"
        + "\n".join(
            f"    - account_id={acct.get('account_id')}, limit={acct.get('limit')}, transactionTotal={acct.get('transactionTotal')}"
            for acct in summary.get('accounts', [])
        )
    )

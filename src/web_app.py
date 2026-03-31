import os

from flask import Flask, render_template

from src.mongo_client import get_mongo_client
from src.transaction_report import get_customer_transaction_summary

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index() -> str:
    error = None
    summaries = []

    try:
        client = get_mongo_client()
        db = client.sample_analytics
        summaries = get_customer_transaction_summary(db)
    except Exception as exc:
        error = str(exc)

    return render_template("index.html", summaries=summaries, error=error)


if __name__ == "__main__":
    port = int(os.getenv("WEB_PORT", "5500"))
    app.run(host="0.0.0.0", port=port, debug=True)

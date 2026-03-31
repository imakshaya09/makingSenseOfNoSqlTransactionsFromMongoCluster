# makingSenseOfNoSqlTransactionsFromMongoCluster

A small Python project that connects to a MongoDB Atlas cluster, reads the `sample_analytics` database, and computes per-customer transaction totals plus account limit exceedance.

## Structure

- `requirements.txt` — Python package dependencies
- `.gitignore` — ignore rules
- `.env.example` — example MongoDB URI configuration
- `src/mongo_client.py` — MongoDB connection helper
- `src/transaction_report.py` — aggregation pipeline and summary logic
- `src/main.py` — executable entrypoint
- `src/web_app.py` — Flask-based web UI
- `src/templates/index.html` — web UI template

## Usage

1. Copy `.env.example` to `.env`
2. Set `MONGODB_URI` to your MongoDB cluster URI.
   - It must begin with `mongodb://` or `mongodb+srv://`.
   - Do not use the Atlas console URL.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the CLI report:

   ```bash
   python -m src.main
   ```

5. Run the web UI:

   ```bash
   python -m src.web_app
   ```

   Then open `http://localhost:5500` in your browser.

   Optional: set a different port via `WEB_PORT` in `.env` or your shell.

## Query behavior

The project uses `customers` as the aggregation root, then joins:
- `accounts` by `account_id`
- `transactions` by `account_id`

It computes:
- total transaction amount per customer
- whether any account limit is less than the customer transaction sum

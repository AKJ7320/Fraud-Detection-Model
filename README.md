# Fraud-Detection-Model
Detect suspicious financial transactions using SQL and Python. Build user-level behavioral features in SQLite, apply Isolation Forest for anomaly detection, and visualize high-risk patterns. Demonstrates unsupervised fraud analytics and SQL-driven data science workflow.

# Author

Adveidh Krishna

Financial Analyst

[LinkedIn](https://www.linkedin.com/in/akthotarath)

## Project Structure

```text
Fraud-Detection-Model/
├── screenshots/
│   ├── fraud_distribution.png
├── data/
│   └── transactions.csv
├── outputs/
│   ├── fraud_scores.csv
│   └── fraud_summary.csv
├── src/
│   ├── __init__.py
│   ├── create_db.py
│   ├── detect_fraud_unsupervised.py
│   ├── queries.sql
│   └── utils.py
├── tests/
├── .github/workflows/ci.yml
├── LICENSE
├── Makefile
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── requirements-lock.txt
```

## Screenshots



![Anomaly score distribution](screenshots/fraud_distribution.png)

## Data and project chronology

The observed transaction snapshot covers **January 1–March 31, 2025** (67,818 records). Its dates were shifted forward uniformly by 366 days, preserving the number of observations, elapsed-day spacing, leap-day separation, transaction amounts and SQL daily-user groupings. No forecast or deployment date is claimed by this retrospective anomaly-ranking pipeline.

The pipeline writes its chart to `screenshots/`, a sibling of the chosen CSV output directory. The default run produces `outputs/*.csv` and `screenshots/fraud_distribution.png`.

The project-development window is **March–August 2026**. All observed transactions precede the earliest project commit. Generated CSV artifacts retain the input transaction identifiers and monetary values.



### Additional model output reports

![Anomaly ranking and transaction amounts](screenshots/anomaly_review.png)

![User review priorities](screenshots/user_review.png)

![Daily transaction activity and review workload](screenshots/transaction_activity.png)

These reports use a global, rank-based top 2% review budget, with transaction ID breaking score ties. This is an illustrative workload selection, not confirmed fraud. User amounts include only selected transactions. Generate them after exporting scores with `python scripts/generate_visual_reports.py`. All transaction dates cover January–March 2025.

# DataForge: Automated Multi-Source SQL Data Pipeline & Quality Validator

A robust, production-ready Python data engineering pipeline designed to ingest raw multi-source datasets, perform programmatic data quality validation and schema enforcement, store clean structured data in a local SQLite relational database, and execute advanced analytical SQL queries.

## 🛠️ Tech Stack
* **Language:** Python
* **Data Manipulation & Ingestion:** Pandas, NumPy
* **Database & Storage:** SQLite (RDBMS)
* **Architecture:** Modular ETL (Extract, Transform, Validate, Load)

---

## 📁 Project Directory Structure
```text
dataforge/
│
├── data/                      # Data storage layer
│   ├── raw/                   # Raw generated datasets (raw_transactions.csv)
│   ├── processed/             # Cleaned and validated records
│   └── warehouse.db           # Local SQLite relational database
│
├── scripts/                   # Core pipeline modules
│   ├── data_generator.py      # Synthetic raw data generator with injected anomalies
│   ├── validator.py           # Programmatic schema validation & anomaly engine
│   └── pipeline.py            # Main orchestrator (ETL + SQL Window Functions)
│
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
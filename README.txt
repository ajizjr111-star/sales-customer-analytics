# Sales & Customer Analytics Dashboard Using Python

This is a runnable demonstration model based on the structure and requirements in the internship report.

## What is included
- `app.py` — interactive dashboard and data-cleaning pipeline
- `data/sales_data.csv` — generated sample sales data with the fields in the report
- `requirements.txt` — Python packages needed
- `run_windows.bat` — optional Windows shortcut to launch the dashboard

## Run it on Windows
1. Install Python 3.10 or newer from https://www.python.org/downloads/
2. Extract this ZIP folder.
3. Open the extracted folder in File Explorer.
4. Double-click `run_windows.bat`.
5. A browser window should open with the dashboard. If it does not, open the URL shown in the terminal (usually http://localhost:8501).

Or run manually from Command Prompt inside this folder:
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Use your own data
The dashboard accepts an optional CSV upload from its left sidebar. Your CSV should contain these columns:
`order_id, order_date, customer_id, category, region, quantity, price, revenue`

## Important data note
The bundled dataset is synthetic demo data, not original company data. It is designed to demonstrate the report's workflow and visual outputs. The report itself labels some figures as illustrative. Replace the sample CSV with authorized real data before making claims about actual business performance.

## Project workflow
Raw CSV -> Pandas cleaning -> EDA and aggregation -> Matplotlib charts -> interactive dashboard -> filtered CSV export.

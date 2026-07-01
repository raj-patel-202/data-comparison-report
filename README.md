# Data Comparison Report Generator

An automated comparison report generator that leverages **DuckDB** to identify mismatched values across corresponding columns of two tabular datasets based on dynamic common IDs. It connects to Excel files via Windows ODBC, executes complex comparisons inside DuckDB's engine, and orchestrates everything through a **FastAPI** web application.

## Key Features
- **Dynamic Composite Keys**: Choose one or multiple columns directly in the web UI to act as the comparison key.
- **Pure DuckDB Execution**: Bypasses Pandas entirely, performing lightning-fast data matching and merging directly within DuckDB SQL.
- **FastAPI Backend**: Serves a dynamic setup page to configure your comparison keys and processes the report seamlessly in the browser.
- **Premium UI Dashboard**: A beautiful HTML/CSS dashboard featuring a glassmorphism theme, dynamic pagination, zoom controls, hover tooltips for column statistics, and color-coded statuses.
- **Excel Export**: Export any individual data slice or the entire multi-tabbed report directly to `.xlsx`. The export logic is powered by a robust backend using `openpyxl`, ensuring accurate cell formatting and column matching.

The project is structured across the following main files:
1. `database.py`: Handles dynamic table name and file discovery using `pyodbc`.
2. `compare.py`: Houses the core DuckDB SQL generation, dynamic composite key validation, hover-stat aggregations, and data cleanup.
3. `main.py`: The FastAPI server that loads environment variables, renders Jinja2 templates, and generates the final HTML output.
4. `static/main.js`: Client-side logic for pagination, Excel export, and Chart.js rendering.

## Quick Setup

1. Create a virtual environment and activate it (for Windows):
```cmd
python -m venv .venv
.venv\Scripts\activate
```
2. Install the required Python packages:
```cmd
pip install -r requirements.txt
```

## How to Use

### 1. Configure Windows ODBC DSNs
The backend connects to the Excel files using Windows ODBC drivers. Before running the report, you must configure two System or User DSNs using the "ODBC Data Sources (64-bit)" administrator tool on Windows:
- Create two DSNs using the `Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)` driver.
- Point each DSN to the respective Excel file you want to compare.

### 2. Setup Environment Variables
Create a `.env` file in the root of the project to store your DSN names:
```env
SOURCE_DSN=your_source_dsn
DESTINATION_DSN=your_target_dsn
```

### 3. Run the Application
Once your DSNs and `.env` file are configured, start the FastAPI server:
```cmd
python main.py
```
This will start the server and **automatically open the setup page in your default web browser** (typically `http://127.0.0.1:8000`).

### 4. Generate the Report
1. On the setup page, select the column(s) you wish to use as your comparison key.
2. Click **Generate Report**.
3. The report will process in the background and automatically redirect to the generated dashboard. You can also view the persistent HTML file saved in `static/report.html`.

### 5. Exporting Data
Once viewing the report, you can click the **Export (.xlsx) ▾** dropdown on any tab to download the exact view you're currently looking at or export the entire workbook!

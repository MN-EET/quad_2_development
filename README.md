# Quad 2.0 - Generation Data Pipeline

Welcome to the code repository for Quad 2.0! This project contains the ETL pipeline used to generate energy generation data for the Minnesota Department of Commerce's State Energy Policy and Conservation Report.

## Table of Contents
- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Creating the DuckDB Database](#creating-the-duckdb-database)
- [Running dbt Transformations](#running-dbt-transformations)
- [Exporting Data](#exporting-data)
- [Updating Data](#updating-data)
- [Testing and Troubleshooting](#testing-and-troubleshooting)
- [Project Structure](#project-structure)
- [Quick Reference](#quick-reference)
- [Data Sources](#data-sources)

---

## Project Overview

The Quad 2.0 Generation Data Pipeline is an ETL system that collects, processes, and exports energy generation data for Minnesota and the MISO region.

### Technology Stack
- **Python 3.12.6** - Data extraction and processing
- **DuckDB** - Embedded analytical database
- **dbt (data build tool)** - SQL-based transformations
- **Pandas** - Data manipulation
- **PowerBI** - Visualization and dashboarding

### Data Flow
1. **Load Raw Data** → Run `scripts/generation/load_generators.py` to fetch PUC and EIA generator data into DuckDB, and optionally run `scripts/generation/load_reis_forecasts.py` to load local forecast Excel files
2. **Transform Data** → Run dbt models to clean and transform raw data into analysis-ready marts
3. **Export Data** → Run `main.py` to export CSV files for PowerBI dashboards

---

## Prerequisites

<details>
<summary><b>Required Software</b></summary>

- **Python 3.12.6 or higher** - [Download here](https://www.python.org/downloads/)
- **Git** - For cloning the repository
- **OneDrive** - Required for PowerBI cloud connections (output files must be stored in OneDrive)
- **PowerBI Desktop** - For connecting to exported data

</details>

<details>
<summary><b>Required API Access</b></summary>

### EIA API Key (Free)

You need a free API key from the U.S. Energy Information Administration.

**To obtain an EIA API key:**
1. Visit https://www.eia.gov/opendata/register.php
2. Register for a free account
3. Check your email for your API key
4. Save this key - you'll add it to your `.env` file during setup

</details>

---

## Setup Instructions

<details>
<summary><b>Step 1: Clone the Repository</b></summary>

```bash
git clone https://github.com/MN-EET/quad_2_development
cd quad_2_development
```

</details>

<details>
<summary><b>Step 2: Create a Virtual Environment</b></summary>

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

</details>

<details>
<summary><b>Step 3: Install Required Packages</b></summary>

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- pandas - Data manipulation
- duckdb - Embedded database
- dbt-duckdb - dbt adapter for DuckDB
- python-dotenv - Environment variable management
- And other required packages

</details>

<details>
<summary><b>Step 4: Configure Environment Variables</b></summary>

Create a `.env` file in the project root directory:

1. Create a file named `.env` in the `quad_2_development` directory
2. Add your EIA API key:

```bash
EIA_API_KEY=your_api_key_here
```

**Example:**
```bash
EIA_API_KEY=abc123def456ghi789jkl012mno345pq
```

⚠️ **Important:** No spaces around the equals sign!

</details>

<details>
<summary><b>Step 5: Configure Output Directory</b></summary>

### ⚠️ CRITICAL: Output Directory Must Be in OneDrive

Output files **must** be stored in OneDrive for PowerBI cloud connections to work properly.

1. Open `main.py`
2. Update the `destdir` variable to point to your OneDrive folder:

```python
destdir = r'C:\Users\YOUR_USERNAME\OneDrive\quad_data'
```

**Replace:**
- `YOUR_USERNAME` with your Windows username
- `quad_data` with your preferred folder name in OneDrive

3. Create this folder in OneDrive before running the pipeline

</details>

<details>
<summary><b>Step 6: Configure dbt Profiles</b></summary>

### Understanding dbt Profiles

The `profiles.yml` file tells dbt how to connect to your database. 

### ⚠️ IMPORTANT: Where to Save profiles.yml

**This is counterintuitive:** The `profiles.yml` file does NOT go in your project folder. Instead, it must be saved in a `.dbt` folder in your home directory.

**File Location:**

- **Windows:** `C:\Users\YOUR_USERNAME\.dbt\profiles.yml`
- **Mac/Linux:** `~/.dbt/profiles.yml` (which expands to `/Users/YOUR_USERNAME/.dbt/profiles.yml`)

**Setup Steps:**

1. Create the `.dbt` folder in your home directory if it doesn't exist:

   **Windows:**
   ```bash
   mkdir %USERPROFILE%\.dbt
   ```

   **Mac/Linux:**
   ```bash
   mkdir ~/.dbt
   ```

2. Copy the `profiles.yml` file from `generator_dbt_project/profiles.yml` to the `.dbt` folder:

   **Windows:**
   ```bash
   copy generator_dbt_project\profiles.yml %USERPROFILE%\.dbt\profiles.yml
   ```

   **Mac/Linux:**
   ```bash
   cp generator_dbt_project/profiles.yml ~/.dbt/profiles.yml
   ```

**Note:** Even though `profiles.yml` is in your home directory, the database paths inside it (like `../duckdb_storage/dev.duckdb`) are still relative to your **project directory**, not to where the profiles.yml file is stored. This is how dbt works by design.

### Default Configuration

The profiles.yml should contain the following settings:

```yaml
generator_dbt_project:  
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../duckdb_storage/dev.duckdb
      threads: 1
    prod:
      type: duckdb
      path: ../duckdb_storage/prod.duckdb
      threads: 1
```

### What This Configuration Does

- **target: dev** - By default, dbt will use the `dev` database for development work
- **type: duckdb** - Specifies that we're using DuckDB as our database
- **path: ../duckdb_storage/dev.duckdb** - Points to the DuckDB database file (relative to the project directory, not the profiles.yml location)
- **threads: 1** - Number of concurrent models dbt will run (1 is fine for this project size)

### When to Switch to Production

To use the production database instead of development:
1. Open `~/.dbt/profiles.yml` (in your home directory)
2. Change `target: dev` to `target: prod`
3. Or use the command line flag: `dbt run --target prod`

</details>

---

## Creating the DuckDB Database

<details>
<summary><b>What is DuckDB?</b></summary>

DuckDB is a fast, embedded analytical database that runs directly within your application - no separate server required. Think of it as "SQLite for analytics."

### Why DuckDB for This Project?

- **Embedded** - The entire database is a single file (`.duckdb`) that lives in your project folder
- **Fast** - Optimized for analytical queries and data transformations
- **Simple** - No installation or server configuration needed
- **Portable** - Easy to share and backup (just copy the `.duckdb` file)

### Development vs Production Databases

This project uses two separate database files:

- **dev.duckdb** - For testing and development work
  - Use this when experimenting with new transformations
  - Safe to delete and rebuild without affecting production data
  
- **prod.duckdb** - For final, production-ready data
  - Use this for data that will be exported to PowerBI dashboards
  - Contains the "official" data that stakeholders rely on

By maintaining separate databases, you can test changes in `dev` before applying them to `prod`.

</details>

<details>
<summary><b>Understanding the Database Creation Process</b></summary>

The DuckDB database stores raw generator capacity data from EIA and PUC sources. The `scripts/generation/load_generators.py` script:

- Downloads the latest PUC Distributed Energy Resources (DER) Excel file
- Downloads the latest EIA Form 860 generator data (ZIP file)
- Creates a DuckDB database at `duckdb_storage/dev.duckdb` (or `prod.duckdb`)
- Loads data into tables named `raw_puc_der` and `raw_eia_860_generators`

Additionally, the `scripts/generation/load_reis_forecasts.py` script loads local forecast Excel files into the database's `main_forecast` schema.

</details>

<details>
<summary><b>Updating Data Source URLs</b></summary>

### ⚠️ IMPORTANT: Verify URLs Before Running

Before running `scripts/generation/load_generators.py`, verify that the URLs point to the most recent data.

Open `scripts/generation/load_generators.py` and check:
- **PUC URL:** Check https://mn.gov/puc/activities/economic-analysis/distributed-energy/der-data-dashboard/ for the latest file
- **EIA URL:** Check https://www.eia.gov/electricity/data/eia860/ for the latest year's data

Update the `report_year` parameter to match the data year (typically the previous calendar year).

</details>

<details>
<summary><b>Running load_generators.py</b></summary>

With your virtual environment activated and URLs verified:

```bash
python scripts/generation/load_generators.py
```

**Expected output:**
```
Using DuckDB file at: /path/to/quad_2_development/duckdb_storage/dev.duckdb
Table 'raw_puc_der' created.
Table 'raw_eia_860_generators' created.
```

The script will:
1. Create the `duckdb_storage/` directory if it doesn't exist
2. Create `dev.duckdb` (or `prod.duckdb` depending on the env parameter)
3. Create the `main_generators` schema in the database
4. Load raw data into tables with automatic timestamps

### Development vs Production

The `env` parameter controls which database to use:
- `env="dev"` → Creates/uses `duckdb_storage/dev.duckdb` (recommended for testing)
- `env="prod"` → Creates/uses `duckdb_storage/prod.duckdb` (for final production data)

</details>

<details>
<summary><b>Loading Forecast Data (Optional)</b></summary>

### What is load_reis_forecasts.py?

The `scripts/generation/load_reis_forecasts.py` script loads local Excel forecast files into the DuckDB database under the `main_forecast` schema. These are internally-produced forecast files that your team creates and stores on a shared drive or local directory.

### When to run this script

Run this script if you have forecast Excel files that need to be transformed by dbt and exported. This is separate from the generator capacity data pipeline.

### Configuring file paths

1. Open `scripts/generation/load_reis_forecasts.py`
2. Update the `excel_files` list with paths to your local forecast Excel files:

```python
excel_files = [
    r"C:\path\to\your\MN Consumers 2024.xlsx",
    r"C:\path\to\your\Consumption 2024.xlsx"
]
```

3. Update the `env` parameter if needed (`"dev"` or `"prod"`)

### Running the script

```bash
python scripts/generation/load_reis_forecasts.py
```

**Expected output:**
```
Using DuckDB file at: /path/to/quad_2_development/duckdb_storage/prod.duckdb
Loading MN Consumers 2024.xlsx into main_forecast.mn_consumers_2024
Loading Consumption 2024.xlsx into main_forecast.consumption_2024
All main_forecast Excel files loaded.
```

The script will:
- Create the `main_forecast` schema if it doesn't exist
- Load each Excel file as a table (filename becomes table name)
- Clean column names (lowercase, underscores instead of spaces)

</details>

---

## Running dbt Transformations

<details>
<summary><b>Introduction to dbt (For New Users)</b></summary>

### What is dbt?

dbt (data build tool) transforms data in your database using SQL. Instead of writing Python code to clean and combine data, you write SQL SELECT statements that dbt runs in the correct order.

### How does dbt work in this project?

The dbt project is located in the `generator_dbt_project/` folder. It contains SQL files that define transformations:

- **Staging models** - Clean and standardize raw data
- **Dimension models** - Create lookup tables for categorization
- **Mart models** - Create final analysis-ready tables

### Transformation Pipeline

```
Raw tables (from load_generators.py and load_reis_forecasts.py)
  ↓
Staging models (stg_puc__generators, stg_eia__generators)
  ↓
Technology-specific staging (stg_eia__solar, stg_puc__solar, etc.)
  ↓
Final mart tables (mart_combined__solar_capacity, etc.)
```

</details>

<details>
<summary><b>Running dbt Commands</b></summary>

### ⚠️ PREREQUISITE: Database Must Exist First

**Before running any dbt commands**, you must create and populate the DuckDB database by running the Python data loading scripts:

1. **Required:** Run `python scripts/generation/load_generators.py` to load generator data
2. **Optional:** Run `python scripts/generation/load_reis_forecasts.py` to load forecast data

dbt transforms data that already exists in the database - it cannot run on an empty database. If you skip this step, dbt will fail with errors like "relation does not exist."

---

Navigate to the dbt project directory:

```bash
cd generator_dbt_project
```

### Step 1: Install dbt Dependencies (First Time Only)

If the project uses any dbt packages:

```bash
dbt deps
```

> **Note:** If there is no `packages.yml` file, you can skip this step.

### Step 2: Debug and Verify Configuration

Verify that dbt can connect to the DuckDB database:

```bash
dbt debug
```

This checks:
- Python version
- dbt version
- Database connection (should find `../duckdb_storage/dev.duckdb`)
- Project configuration

✅ **Expected:** All checks should pass with `OK` status.

### Step 3: Run All dbt Models

Execute all transformations to create the mart tables:

```bash
dbt run
```

This will:
- Compile all SQL models
- Execute them in the correct dependency order
- Create views and tables in the DuckDB database

✅ **Expected:** Summary showing models built successfully.

### Step 4: Return to Project Root

```bash
cd ..
```

</details>

<details>
<summary><b>Running Specific Models</b></summary>

You can run specific models or groups of models:

**Run a single model:**
```bash
dbt run --select mart_combined__solar_capacity
```

**Run all models in a folder:**
```bash
dbt run --select solar.marts
```

**Run a model and all its upstream dependencies:**
```bash
dbt run --select +mart_combined__solar_capacity
```

</details>

<details>
<summary><b>Verifying dbt Outputs</b></summary>

After running dbt, verify that the mart tables were created:

```python
python
>>> import duckdb
>>> db = duckdb.connect('duckdb_storage/dev.duckdb')
>>> db.execute('SHOW TABLES FROM main_generators').fetchall()
>>> exit()
```

You should see tables like:
- `mart_combined__solar_capacity`
- `mart_total__wind_capacity`
- `mart_combined__storage_capacity`

</details>

---

## Exporting Data

<details>
<summary><b>Understanding main.py</b></summary>

The `main.py` file contains function calls to various data export scripts. Each function either:
- Fetches data from EIA APIs, OR
- Queries transformed data from DuckDB

Then processes and exports CSV files to your configured output directory.

### Types of Export Scripts

**1. API Data Fetchers** - Fetch data directly from EIA APIs:
- `fetch_generation` - Annual electricity generation by fuel type
- `fetch_monthly_gen` - Monthly generation data
- `fetch_henry_hub` - Natural gas spot prices
- `fetch_miso_hourly` - Hourly generation by fuel type for MISO
- `fetch_miso_annual` - Annual MISO generation summary
- `fetch_nuclear_facilities` - Operating nuclear power plants
- `fetch_battery_capacity` - Battery storage capacity
- `fetch_miso_queue` - MISO interconnection queue projects

**2. DuckDB Mart Exporters** - Query transformed data from dbt marts:
- `fetch_solar_capacity` - Exports `mart_combined__solar_capacity`
- `fetch_wind_capacity` - Exports `mart_total__wind_capacity`
- `fetch_storage_capacity` - Exports `mart_combined__storage_capacity`
- `fetch_net_generation_forecast` - Exports forecast data
- `fetch_mn_consumers_forecast` - Exports consumer forecast data

</details>

<details>
<summary><b>Running Export Scripts</b></summary>

### Step 1: Edit main.py

Open `main.py` in a text editor. You'll see that most function calls are commented out with `#` symbols.

### Step 2: Uncomment Desired Functions

Remove the `#` from the beginning of the lines for functions you want to run.

**Example - To run all exports:**
```python
fetch_generation(eia_key, destdir)
fetch_monthly_gen(eia_key, destdir)
fetch_henry_hub(eia_key, destdir)
# ... and so on
```

**Example - To run only specific exports:**
```python
# fetch_generation(eia_key, destdir)  # Commented out
fetch_solar_capacity(db, destdir)  # Active
fetch_wind_capacity(db, destdir)  # Active
```

### Step 3: Update Database Path for Mart Exports

For functions that query DuckDB (like `fetch_solar_capacity`), uncomment the database path line:

```python
db = 'duckdb_storage/prod.duckdb'  # or dev.duckdb for testing
```

### Step 4: Run main.py

Save your changes and run:

```bash
python main.py
```

The script will:
- Fetch data from APIs or query DuckDB
- Process and format the data
- Write CSV files to your OneDrive output directory

</details>

<details>
<summary><b>Verifying Exported Files</b></summary>

After running `main.py`, check your OneDrive output directory. You should see CSV files like:

- `electricity_generation.csv`
- `monthly_electricity_generation.csv`
- `henry_hub.csv`
- `solar_capacity.csv`
- `wind_capacity.csv`
- `storage_capacity.csv`
- And more, depending on which functions you ran

</details>

---

## Updating Data

<details>
<summary><b>Updating Generator Capacity Data (Annual)</b></summary>

When new data becomes available (typically annually for EIA and PUC data):

### Step 1: Check for New Data Sources

- **PUC Data:** Visit https://mn.gov/puc/activities/economic-analysis/distributed-energy/der-data-dashboard/
- **EIA Data:** Visit https://www.eia.gov/electricity/data/eia860/

### Step 2: Update scripts/generation/load_generators.py

Open `scripts/generation/load_generators.py` and update:
- The PUC URL to the latest file
- The EIA URL to the latest year (e.g., `eia8602025.zip`)
- The `report_year` parameter to the new year

### Step 3: Reload Database

```bash
python scripts/generation/load_generators.py
```

If you have forecast files to update:
```bash
python scripts/generation/load_reis_forecasts.py
```

### Step 4: Re-run dbt Transformations

```bash
cd generator_dbt_project
dbt run
cd ..
```

### Step 5: Re-export Data

```bash
python main.py
```

</details>

<details>
<summary><b>Updating API-Based Data (As Needed)</b></summary>

For data that comes directly from EIA APIs (generation, prices, etc.), simply re-run `main.py` with the appropriate functions uncommented. The scripts automatically query the latest available data from the APIs.

</details>

---

## Testing and Troubleshooting

<details>
<summary><b>Verifying Your Setup</b></summary>

### 1. Check DuckDB Database Exists

```bash
ls duckdb_storage/
```

**Expected:** You should see `dev.duckdb` or `prod.duckdb`

### 2. Check Database Contains Data

```python
python
>>> import duckdb
>>> db = duckdb.connect('duckdb_storage/dev.duckdb')
>>> db.execute('SELECT COUNT(*) FROM main_generators.raw_puc_der').fetchone()
>>> db.execute('SELECT COUNT(*) FROM main_generators.raw_eia_860_generators').fetchone()
>>> exit()
```

**Expected:** Non-zero row counts for both tables

### 3. Check dbt Models Created Tables

```python
python
>>> import duckdb
>>> db = duckdb.connect('duckdb_storage/dev.duckdb')
>>> db.execute('SHOW TABLES FROM main_generators').fetchall()
>>> exit()
```

**Expected:** Tables including `mart_combined__solar_capacity`, `mart_total__wind_capacity`, `mart_combined__storage_capacity`

### 4. Check CSV Files Were Exported

Navigate to your OneDrive output directory and verify that CSV files exist.

</details>

<details>
<summary><b>Common Issues and Solutions</b></summary>

### Issue: ModuleNotFoundError when running scripts

**Solution:** Make sure your virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Issue: API request returns 401 Unauthorized

**Solution:** Check that your EIA API key is correctly set in the `.env` file. Make sure there are no spaces around the equals sign:
```bash
EIA_API_KEY=your_key_here
```

### Issue: dbt debug shows database connection failed

**Solution:** Make sure you've run `scripts/generation/load_generators.py` first to create the DuckDB database. Verify the database exists at `duckdb_storage/dev.duckdb`

### Issue: dbt run fails with "relation does not exist"

**Solution:** The raw tables haven't been created yet. Run `scripts/generation/load_generators.py` to create and populate the raw data tables before running dbt.

### Issue: CSV files are empty or missing data

**Solution:** Check that:
- Your API key is valid and working
- The URLs in `scripts/generation/load_generators.py` point to valid, current data files
- dbt models completed successfully before running mart export functions

### Issue: PowerBI can't find the CSV files

**Solution:** Verify that:
- The output directory path in `main.py` is an OneDrive location
- OneDrive has synced the files (check the OneDrive icon in your system tray)
- The file paths in PowerBI match your actual OneDrive directory structure

</details>

---

## Project Structure

```
quad_2_development/
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
├── main.py                       # Main export script
├── README.md                     # This file
├── duckdb_storage/               # DuckDB databases
│   ├── dev.duckdb                # Development database
│   └── prod.duckdb               # Production database
├── scripts/                      # Data extraction scripts
│   └── generation/               # Generation data scripts
│       ├── load_generators.py    # Database creation script (PUC/EIA data)
│       ├── load_reis_forecasts.py # Forecast data loader (local Excel files)
│       ├── build_generator_file.py # Database builder function
│       ├── electricity_generation.py
│       ├── monthly_generation.py
│       ├── natural_gas.py
│       ├── miso_hourly.py
│       ├── miso_annual.py
│       ├── nuclear_facilities.py
│       ├── battery_capacity.py
│       ├── miso_queue.py
│       ├── qry_solar_mart.py     # Exports dbt mart
│       ├── qry_wind_mart.py      # Exports dbt mart
│       ├── qry_storage_mart.py   # Exports dbt mart
│       ├── qry_net_generation_forecast_mart.py
│       └── qry_mn_consumers_forecast_mart.py
└── generator_dbt_project/        # dbt transformation project
    ├── dbt_project.yml            # dbt project config
    ├── profiles.yml               # dbt database connection
    └── models/                   # SQL transformation models
        ├── sources.yml            # Data source definitions
        ├── common/                # Shared models
        ├── solar/                 # Solar-specific models
        │   ├── staging/
        │   ├── dimensions/
        │   └── marts/
        ├── wind/                  # Wind-specific models
        ├── storage/               # Storage-specific models
        └── consumer_forecast/     # Forecast models
```

---

## Quick Reference

<details>
<summary><b>Complete Workflow Checklist</b></summary>

### Initial Setup (One Time)
1. Clone repository
2. Create and activate virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Get EIA API key from https://www.eia.gov/opendata/register.php
5. Create `.env` file with API key
6. Configure output directory in `main.py` (OneDrive location)

### Creating/Updating Database and Exporting Data
1. Update URLs in `scripts/generation/load_generators.py` (check for latest data)
2. Run: `python scripts/generation/load_generators.py`
3. (Optional) Update file paths in `scripts/generation/load_reis_forecasts.py` and run: `python scripts/generation/load_reis_forecasts.py`
4. Navigate to dbt project: `cd generator_dbt_project`
5. Run dbt: `dbt run`
6. Return to project root: `cd ..`
7. Edit `main.py` to uncomment desired export functions
8. Run: `python main.py`
9. Connect PowerBI to exported CSV files in OneDrive

</details>

<details>
<summary><b>Common Commands</b></summary>

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Load database with latest generator data
python scripts/generation/load_generators.py

# Load database with forecast data (optional)
python scripts/generation/load_reis_forecasts.py

# Run all dbt models
cd generator_dbt_project && dbt run && cd ..

# Export data to CSV
python main.py

# Verify database connection
cd generator_dbt_project && dbt debug && cd ..
```

</details>

<details>
<summary><b>Key File Locations</b></summary>

- **DuckDB database:** `duckdb_storage/dev.duckdb`
- **API key:** `.env` file (`EIA_API_KEY=...`)
- **Output directory config:** `main.py` (`destdir` variable)
- **Generator data source URLs:** `scripts/generation/load_generators.py`
- **Forecast data file paths:** `scripts/generation/load_reis_forecasts.py`
- **dbt configuration:** `generator_dbt_project/dbt_project.yml`
- **Database connection:** `generator_dbt_project/profiles.yml`

</details>

---

## Data Sources

<details>
<summary><b>EIA (U.S. Energy Information Administration)</b></summary>

- **API Documentation:** https://www.eia.gov/opendata/
- **Form 860 (Generator Data):** https://www.eia.gov/electricity/data/eia860/
- **Register for API Key:** https://www.eia.gov/opendata/register.php

</details>

<details>
<summary><b>Minnesota PUC (Public Utilities Commission)</b></summary>

- **DER Data Dashboard:** https://mn.gov/puc/activities/economic-analysis/distributed-energy/der-data-dashboard/
- **Data:** Distributed Energy Resources reported by utilities

</details>

<details>
<summary><b>MISO (Midcontinent Independent System Operator)</b></summary>

- **Interconnection Queue:** https://www.misoenergy.org/planning/generator-interconnection/GI_Queue/
- **API Endpoint:** https://www.misoenergy.org/api/giqueue/getprojects

</details>

<details>
<summary><b>Regional Energy Information System (REIS)</b></summary>

- **Source:** Minnesota Department of Commerce
- **Data:** Electricity forecasts based on utility data collected and processed directly by the Minnesota Department of Commerce
- **Format:** Excel files stored locally or on shared drives
- **Usage:** Loaded into the DuckDB database using `scripts/generation/load_reis_forecasts.py`
- **Note:** These are internally-produced datasets specific to Minnesota energy planning and analysis

</details>

---

## Support

For questions or support, contact the Minnesota Department of Commerce  
**Energy and Environmental Technologies Division**

---

## License

This project is maintained by the Minnesota Department of Commerce.
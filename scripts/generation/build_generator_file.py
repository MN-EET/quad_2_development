import pandas as pd
from requests import get
import zipfile
import io
import janitor
import duckdb
from pathlib import Path
import os

"""
This function pulls data from both the PUC's Distributed Energy Resources file and EIA's 860 generator file. 
After some small transformations, these tables are loaded into the generator_database.duckdb file, where they are 
further transformed and used for the solar capacity dashboards and the capacity additions and retirements dashboard.

PUC DER table is available here: https://mn.gov/puc/activities/economic-analysis/distributed-energy/der-data-dashboard/
EIA 860 Files available here: https://www.eia.gov/electricity/data/eia860/
"""


def build_generator_table(puc_url: str, eia_url: str, puc_table_name: str,
                          eia_table_name: str, report_year: int, env="dev"  # or prod
                          ):
    # Read in latest version of the PUC's DER file
    raw_der = pd.read_excel(puc_url)

    # Clean up the DER file
    der_table = raw_der.clean_names().copy()
    der_table.loc[:, 'report_year'] = report_year

    # Pull EIA 860 generators table

    response = get(eia_url)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Find the file that starts with "3_1_Generator"
        eia_table = next(
            (name for name in z.namelist() if name.startswith("3_1_Generator") and name.endswith(".xlsx")),
            None
        )

        if eia_table is None:
            raise FileNotFoundError("No file starting with '3_1_Generator' found in the ZIP archive.")

        with z.open(eia_table) as file:
            eia_table = pd.read_excel(file, skiprows=1)

    # clean up names and create report year column
    eia_table = eia_table.clean_names().copy()
    eia_table.loc[:, 'report_year'] = report_year

    # Coerce utlity IDs to numeric to scrap the comment that is typically at the bottom of the table
    eia_table['utility_id'] = pd.to_numeric(eia_table['utility_id'], errors="coerce")

    # DUCKDB COERCION PREP: Clean whitespace-only strings to None for all object columns
    # This allows DuckDB to handle type conversion automatically during INSERT
    for col in eia_table.select_dtypes(include=['object']).columns:
        eia_table[col] = eia_table[col].replace(r'^\s*$', None, regex=True)

    # Drop rows with null utility IDs
    eia_table = eia_table.dropna(subset=['utility_id'])

    # Create database path
    # Resolve the script path and the project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[1]  # adjust depending on how deep your script is

    # Define the database folder relative to the root
    storage_dir = project_root / "duckdb_storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Full path to the DuckDB file
    db_path = storage_dir / f"{env}.duckdb"
    print("Using DuckDB file at:", db_path)

    # Choose between dev and prod
    if env not in ("dev", "prod"):
        raise ValueError("env must be either 'dev' or 'prod'")

    db = duckdb.connect(str(db_path))
    # create generators schema
    db.execute("CREATE SCHEMA IF NOT EXISTS main_generators")

    # Helper function to create or append a table
    def upsert_table(df, table_name):
        # DUCKDB COERCION STEP 1: Register the pandas DataFrame as a temporary view
        # DuckDB will infer types from the pandas dtypes
        db.register('temp_view', df)

        table_exists = db.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'main_generators'
                AND table_name = '{table_name}'
        """).fetchone()[0] > 0

        if not table_exists:
            # DUCKDB COERCION STEP 2: CREATE TABLE - DuckDB creates schema from temp_view
            # Type conversion happens automatically based on pandas dtypes
            db.execute(
                f"CREATE TABLE main_generators.{table_name} AS SELECT *, CURRENT_TIMESTAMP AS created_at FROM temp_view")
            print(f"Table '{table_name}' created.")
        else:
            # DUCKDB COERCION STEP 3: INSERT - DuckDB automatically casts temp_view columns
            # to match the existing table schema. This is where the magic happens!
            # DuckDB will try to convert types intelligently (e.g., string '123' -> integer 123)
            db.execute(f"INSERT INTO main_generators.{table_name} SELECT *, CURRENT_TIMESTAMP AS created_at FROM temp_view")
            print(f"Data appended to existing table '{table_name}'.")

    # Load PUC DER table
    upsert_table(der_table, puc_table_name)

    # Load EIA table
    upsert_table(eia_table, eia_table_name)

    db.close()
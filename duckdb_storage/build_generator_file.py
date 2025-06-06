import pandas as pd
from requests import get
import zipfile
import io
import janitor
import duckdb
import os

"""
This function pulls data from both the PUC's Distributed Energy Resources file and EIA's 860 generator file. 
After some small transformations, these tables are loaded into the generator_database.duckdb file, where they are 
further transformed and used for the solar capacity dashboards and the capacity additions and retirements dashboard.

PUC DER table is available here: https://mn.gov/puc/activities/economic-analysis/distributed-energy/der-data-dashboard/
EIA 860 Files available here: https://www.eia.gov/electricity/data/eia860/
"""
def build_generator_table(puc_url: str, eia_url: str, puc_table_name: str, eia_table_name: str, report_year: int):
    # Read in latest version of the PUC's DER file
    raw_der = pd.read_excel(puc_url)

    # Clean up the DER file
    der_table = raw_der.clean_names().copy()
    der_table.loc[:, 'report_year'] = report_year

    # Pull EIA 860 generators table

    response = get(eia_url)
    #zip_bytes = io.BytesIO(response.content)

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
    eia_table['utility_id'] = pd.to_numeric(eia_table['utility_id'], errors = "coerce")

    # Drop rows with null utility IDs
    eia_table = eia_table.dropna(subset = ['utility_id'])

    # Create database path
    base_dir = os.path.dirname(__file__)
    storage_dir = os.path.join(base_dir, 'duckdb_storage')
    os.makedirs(storage_dir, exist_ok=True)
    db_path = os.path.join(os.path.dirname(__file__), 'generator_database.duckdb')
    db = duckdb.connect(db_path)

    # Check if puc_table name already exists
    table_exists = db.execute(f"""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_name = '{puc_table_name}'
    """).fetchone()[0] > 0

    # Register DataFrame as a temp view
    db.register('der_table_view', der_table)

    if not table_exists:
    # Create puc der table in duckdb from the der_table
        db.execute(f"CREATE TABLE {puc_table_name} AS SELECT *, CURRENT_TIMESTAMP AS created_at FROM der_table_view")
        print(f"Table '{puc_table_name}' created.")
    else:
        db.execute(f"""
               INSERT INTO {puc_table_name}
               SELECT *, CURRENT_TIMESTAMP AS created_at 
               FROM der_table_view
           """)
        print(f"Data appended to existing table '{puc_table_name}'.")

    # Write EIA table
    table_exists = db.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = '{eia_table_name}'
        """).fetchone()[0] > 0

    # Register DataFrame as a temp view
    db.register('eia_table_view', eia_table)

    if not table_exists:
    # Create EIA 860 table in duckdb from the der_table
        db.execute(f"CREATE TABLE {eia_table_name} AS SELECT *, CURRENT_TIMESTAMP AS created_at FROM eia_table_view")
        print(f"Table '{eia_table_name}' created.")
    else:
        db.execute(f"""
                      INSERT INTO {eia_table_name}
                      SELECT *, CURRENT_TIMESTAMP AS created_at 
                      FROM eia_table_view
                  """)
        print(f"Data appended to existing table '{eia_table_name}'.")

    db.close()
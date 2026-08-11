import pandas as pd
import duckdb
import os
from dotenv import load_dotenv
from pathlib import Path

def load_forecast_excels(file_paths, env="dev"):
    """
    Load multiple Excel files into a DuckDB schema called 'main_forecast'.
    Uses the same project-root-based path setup as the generator ETL script.

    Parameters:
        file_paths (list[Path | str]): List of paths to Excel files.
        env (str): Either "dev" or "prod".
    """

    # Resolve project root (adjust parents[x] if script lives deeper)
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[int(os.getenv("PROJECT_ROOT_DEPTH", "1"))]

    # Define DuckDB path relative to root
    storage_dir = project_root / "duckdb_storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    db_path = storage_dir / f"{env}.duckdb"
    print("Using DuckDB file at:", db_path)

    # Connect to DuckDB
    db = duckdb.connect(str(db_path))

    # Create schema if needed
    db.execute("CREATE SCHEMA IF NOT EXISTS main_forecast")

    # Loop through Excel files
    for file_path in file_paths:
        file_path = Path(file_path)
        table_name = file_path.stem.lower().replace(" ", "_")  # filename → table name

        print(f"Loading {file_path.name} into main_forecast.{table_name}")

        # Load Excel
        df = pd.read_excel(file_path)

        # Clean column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Register + write
        db.register("tmp_view", df)
        db.execute(f"CREATE OR REPLACE TABLE main_forecast.{table_name} AS SELECT * FROM tmp_view")

    db.close()
    print("All main_forecast Excel files loaded.")

if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]

    excel_files = [
        r"I:\Enrgy_div\SEO\CleanEnegyTechUnit\CET Projects\Data Repository\REIS Work\Electric Forecasts\Electric-Forecasts\Consumers\MN Consumers 2024.xlsx",
        r"I:\Enrgy_div\SEO\CleanEnegyTechUnit\CET Projects\Data Repository\REIS Work\Electric Forecasts\Electric-Forecasts\Consumption\Consumption 2024 TRADE SECRET.xlsx"
    ]

    load_forecast_excels(excel_files, env="dev")
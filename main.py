
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from dotenv import load_dotenv
from scripts.electricity_generation import fetch_generation
from scripts.monthly_generation import fetch_monthly_gen
from scripts.natural_gas import fetch_henry_hub
from scripts.miso_hourly import fetch_miso_hourly
from scripts.nuclear_facilities import fetch_nuclear_facilities
from scripts.battery_capacity import fetch_battery_capacity
from scripts.miso_queue import fetch_miso_queue
from scripts.qry_solar_mart import fetch_solar_capacity
from scripts.qry_wind_mart import fetch_wind_capacity
from scripts.qry_storage_mart import fetch_storage_capacity
from scripts.miso_annual import fetch_miso_annual
from scripts.qry_net_generation_forecast_mart import fetch_net_generation_forecast
from scripts.qry_mn_consumers_forecast_mart import fetch_mn_consumers_forecast

# Define main

def main():
    # load environmental variables
    load_dotenv()
    eia_key = os.getenv("EIA_API_KEY")

    # Specify directory to write file to
    destdir = r'C:\Users\dduffy\OneDrive - State of Minnesota - MN365\Quad 2.0 Data - Documents\data'

    # fetch generation data
    fetch_generation(eia_key, destdir)

    # fetch monthly generation generation data
    fetch_monthly_gen(eia_key, destdir)

    # fetch henry hub natural gas spot prices
    fetch_henry_hub(eia_key, destdir)

    # fetch miso hourly
    fetch_miso_hourly(eia_key, destdir)

    # fetch annual MISO generation data
    fetch_miso_annual(eia_key, destdir)

    # fetch nuclear facilities
    fetch_nuclear_facilities(eia_key, destdir)

    # fetch battery capacity
    fetch_battery_capacity(eia_key, destdir)

    # fetch MISO queue
    fetch_miso_queue(destdir)

    # fetch solar capacity
    db = 'duckdb_storage/prod.duckdb' # use this database to export all capacity figures
    fetch_solar_capacity(db, destdir)

    # fetch wind capacity
    fetch_wind_capacity(db, destdir)

    # fetch storage capacity
    fetch_storage_capacity(db, destdir)

    # fetch net generation forecast
    fetch_net_generation_forecast(db, destdir)

    # fetch mn consumers forecast
    fetch_mn_consumers_forecast(db, destdir)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

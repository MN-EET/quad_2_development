
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from dotenv import load_dotenv
from scripts.generation.electricity_generation import fetch_generation
from scripts.generation.monthly_generation import fetch_monthly_gen
from scripts.generation.natural_gas import fetch_henry_hub
from scripts.generation.miso_hourly import fetch_miso_hourly
from scripts.generation.nuclear_facilities import fetch_nuclear_facilities
from scripts.generation.battery_capacity import fetch_battery_capacity
from scripts.generation.miso_queue import fetch_miso_queue
from scripts.generation.qry_solar_mart import fetch_solar_capacity
from scripts.generation.qry_wind_mart import fetch_wind_capacity
from scripts.generation.qry_storage_mart import fetch_storage_capacity
from scripts.generation.miso_annual import fetch_miso_annual
from scripts.generation.qry_net_generation_forecast_mart import fetch_net_generation_forecast
from scripts.generation.qry_mn_consumers_forecast_mart import fetch_mn_consumers_forecast
from scripts.consumption.energy_consumption import fetch_energy_consumption

# Define main

def main():
    # load environmental variables
    load_dotenv()
    eia_key = os.getenv("EIA_API_KEY")

    # Specify directory to write file to
    destdir = os.getenv("DESTINATION_DIRECTORY")

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
    #Change back to prod later
    db = 'duckdb_storage/dev.duckdb' # use this database to export all capacity figures
    fetch_solar_capacity(db, destdir)

    # fetch wind capacity
    fetch_wind_capacity(db, destdir)

    # fetch storage capacity
    fetch_storage_capacity(db, destdir)

    # fetch net generation forecast
    fetch_net_generation_forecast(db, destdir)

    # fetch mn consumers forecast
    fetch_mn_consumers_forecast(db, destdir)

    # fetch energy consumption
    fetch_energy_consumption(eia_key, destdir)

if __name__ == '__main__':
    main()

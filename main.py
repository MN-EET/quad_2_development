
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from dotenv import load_dotenv
from scripts.electricity_generation import fetch_generation
from scripts.monthly_generation import fetch_monthly_gen
from scripts.natural_gas import fetch_henry_hub
from scripts.miso_hourly import fetch_miso_hourly


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

    # fetch hourly nuclear data
    fetch_miso_hourly(eia_key, destdir)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

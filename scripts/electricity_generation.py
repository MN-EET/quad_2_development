import pandas as pd
from requests import get
from setuptools.package_index import user_agent


#import os
#from dotenv import load_dotenv

# load_dotenv()

# load API keys
#eia_key = os.getenv("EIA_API_KEY")

def query_generation(area: str, area_label: str, eia_key: str):
    response = get(
        "https://api.eia.gov/v2/electricity/electric-power-operational-data/data?api_key=" + eia_key + "&data[]=generation&frequency=annual&facets[location][]=" + area + "&frequency=annual&facets[sectorid][]=99").json()

    raw_generation = pd.json_normalize(response['response']['data'])

    fuels_keep = ["BIO", "HYC", "SUN", "WND", "COW", "NG", "PEL", "NUC", "OTH", "ALL", "AOR"]
    columns_keep = ['period', 'fuelTypeDescription', 'generation', ]

    total_generation = raw_generation.loc[raw_generation['fueltypeid'].isin(fuels_keep), columns_keep]
    total_generation['generation'] = total_generation['generation'].astype(float)

    # subset hydro values to add to renewables

    hydro_values = total_generation.loc[
        total_generation['fuelTypeDescription'] == 'conventional hydroelectric', ['period', 'generation']].rename(
        columns={'generation': 'hydro_generation'}).set_index('period')
    hydro_values['hydro_generation'] = hydro_values['hydro_generation'].astype(float)

    # add renewables and hydro together

    total_generation.loc[total_generation['fuelTypeDescription'] == 'all renewables', 'generation'] += (
        total_generation.loc[total_generation['fuelTypeDescription'] == 'all renewables', 'period'].map(
            hydro_values['hydro_generation'])
    )

    # calculate as percentage of total generation

    total_gen = total_generation.loc[total_generation['fuelTypeDescription'] == 'all fuels']

    total_gen = total_gen.set_index('period')['generation']

    total_generation['percent_generation'] = total_generation['generation'] / total_generation['period'].map(total_gen)

    # clean up names and data types

    total_generation = total_generation.rename(
        columns={'period': 'year', 'fuelTypeDescription': 'fuel_type', 'generation': 'generation_thousand_mwh'})
    total_generation['year'] = total_generation['year'].astype(int)

    # rename fuel types

    new_fuels = {
        'all renewables': 'Renewables',
        'conventional hydroelectric': 'Hydroelectric',
        'all coal products': 'Coal',
        'other': 'Other',
        'petroleum liquids': 'Petroleum Liquids',
        'wind': 'Wind',
        'natural gas': 'Natural Gas',
        'nuclear': 'Nuclear',
        'all fuels': 'All Fuels',
        'biomass': 'Biomass',
        'solar': 'Solar'
    }

    total_generation['fuel_type'] = total_generation['fuel_type'].replace(new_fuels)
    total_generation['area_label'] = area_label

    # create label in latest year that is formatted as a percent for each fuel type

    max_year = total_generation['year'].max()

    total_generation['percent_label'] = total_generation.apply(

        lambda x: f"{round(x['percent_generation'] * 100, 1)}%"
        if x['year'] == max_year
        else None,
        axis=1
    )

    # sort so latest year is first
    total_generation = total_generation.sort_values(by = ['year'], ascending = False)


    return(total_generation)

def fetch_generation(eia_key: str, destdir: str):

    mn_gen = query_generation("MN", "Minnesota", eia_key)
    us_gen = query_generation("US","USA", eia_key)
    total_gen = pd.concat([mn_gen, us_gen])
    total_gen.to_csv(destdir + '/electricity_generation.csv', index=False)
    # # Query EIA
    #
    # response = get("https://api.eia.gov/v2/electricity/electric-power-operational-data/data?api_key=" + eia_key + "&data[]=generation&frequency=annual&facets[location][]=MN&frequency=annual&facets[sectorid][]=99").json()
    #
    # raw_generation = pd.json_normalize(response['response']['data'])
    #
    # # Clean up raw data
    #
    # fuels_keep = ["BIO", "HYC", "SUN", "WND", "COW", "NG", "PEL", "NUC", "OTH", "ALL", "AOR"]
    # columns_keep = ['period', 'fuelTypeDescription', 'generation', ]
    #
    # mn_generation = raw_generation.loc[raw_generation['fueltypeid'].isin(fuels_keep), columns_keep]
    # mn_generation['generation'] = mn_generation['generation'].astype(float)
    #
    # # subset hydro values to add to renewables
    #
    # hydro_values = mn_generation.loc[mn_generation['fuelTypeDescription'] == 'conventional hydroelectric', ['period', 'generation']].rename(columns = {'generation': 'hydro_generation'}).set_index('period')
    # hydro_values['hydro_generation'] = hydro_values['hydro_generation'].astype(float)
    #
    # #add renewables and hydro together
    #
    # mn_generation.loc[mn_generation['fuelTypeDescription'] == 'all renewables', 'generation'] += (
    #     mn_generation.loc[mn_generation['fuelTypeDescription'] == 'all renewables', 'period'].map(hydro_values['hydro_generation'])
    # )
    #
    # # calculate as percentage of total generation
    #
    # total_gen = mn_generation.loc[mn_generation['fuelTypeDescription'] == 'all fuels']
    #
    # total_gen = total_gen.set_index('period')['generation']
    #
    # mn_generation['percent_generation'] = mn_generation['generation'] / mn_generation['period'].map(total_gen)
    #
    # # clean up names and data types
    #
    # mn_generation = mn_generation.rename(columns = {'period': 'year', 'fuelTypeDescription': 'fuel_type', 'generation': 'generation_thousand_mwh'})
    # mn_generation['year'] = mn_generation['year'].astype(int)
    #
    # # rename fuel types
    #
    # new_fuels = {
    #     'all renewables': 'Renewables',
    #     'conventional hydroelectric': 'Hydroelectric',
    #     'all coal products': 'Coal',
    #     'other': 'Other',
    #     'petroleum liquids': 'Petroleum Liquids',
    #     'wind': 'Wind',
    #     'natural gas': 'Natural Gas',
    #     'nuclear': 'Nuclear',
    #     'all fuels': 'All Fuels',
    #     'biomass': 'Biomass',
    #     'solar': 'Solar'
    # }
    #
    # mn_generation['fuel_type'] = mn_generation['fuel_type'].replace(new_fuels)

    # set destination directory to upload to sharepoint
    # destdir = r'C:\Users\dduffy\OneDrive - State of Minnesota - MN365\Quad 2.0 Data - Documents\data'

    #mn_generation.to_csv(destdir + '/mn_electricity_generation.csv', index = False)


import pandas as pd
from requests import get

def fetch_monthly_gen(eia_key: str, destdir: str):

    # query EIA for monthly coal generation data in Minnesota
    response = get(
        "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key=" + eia_key + "&frequency=monthly&data[0]=generation&facets[fueltypeid][]=COW&facets[location][]=MN&facets[sectorid][]=99&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000").json()

    # normalize response from EIA
    coal_data = pd.json_normalize(response['response']['data'])

    # grab columns that we need and convert data types

    coal_data = coal_data[['period', 'generation']]
    coal_data['period'] = pd.to_datetime(coal_data['period'], format='%Y-%m')
    coal_data = coal_data.astype({'generation': float})

    # write file
    coal_data.to_csv(destdir + '/monthly_coal_generation.csv', index=False)

import pandas as pd
from requests import get

def consumption_query(series_id: str, eia_key: str):

    response = get(
            "https://api.eia.gov/v2/seds/data/?frequency=annual&data[0]=value&api_key=" +
             eia_key +
            "&facets[seriesId][]=" +
             series_id +
            "&facets[stateId][]=MN&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000")

    data_return = pd.json_normalize(response.json()['response']['data'])

    return(data_return)

def fetch_energy_consumption(eia_key: str, destdir: str):
    petro = consumption_query("PMTCB", eia_key)
    imports = consumption_query("ELNIB", eia_key)
    coal = consumption_query("CLTCB", eia_key)
    net_interstate = consumption_query("ELISB", eia_key)
    renewables = consumption_query("RETCB", eia_key)
    gas = consumption_query("NNTCB", eia_key)
    nuclear = consumption_query("NUETB", eia_key)
    total = consumption_query("TETCB", eia_key)

    # subset total and rename value
    total_subset = total[["period", "value"]]
    total_subset = total_subset.rename(columns={"value": "total_consumption"})

    consumption = pd.concat([petro, imports, coal, net_interstate, renewables, gas, nuclear, total], ignore_index=True)
    consumption = consumption.merge(total_subset, on="period")
    consumption = consumption.astype({"period": int, "value": float, "total_consumption": float})
    consumption['percent'] = consumption["value"] / consumption["total_consumption"]

    # Change series names and rename column

    consumption_categories = {
        'All petroleum products, excluding biofuels, total consumption': 'Petroleum',
        'Net imports of electricity into the United States': 'Net Imports',
        'Coal total consumption': 'Coal',
        'Net interstate flow of electricity and associated losses (negative indicates flow out of state)': 'Interstate Flow',
        'Renewable energy total consumption': 'Renewables',
        'Natural gas total consumption (excluding supplemental gaseous fuels)': 'Natural Gas',
        'Nuclear energy consumed for electricity generation, total': 'Nuclear',
        'Total energy consumption': 'Total Energy Consumption'
    }

    consumption['seriesDescription'] = consumption['seriesDescription'].replace(consumption_categories)

    consumption = consumption.rename(columns={'seriesDescription': 'fuel_type'})

    consumption.to_csv(destdir + "/total_energy_consumption.csv", index = False)


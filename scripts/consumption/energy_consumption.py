import pandas as pd
from requests import get

def consumption_query(series_id: str, area: str, eia_key: str):

    response = get(
            "https://api.eia.gov/v2/seds/data/?frequency=annual&data[0]=value&api_key=" +
             eia_key +
            "&facets[seriesId][]=" +
             series_id +
            "&facets[stateId][]=" +
            area +
            "&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000")

    data_return = pd.json_normalize(response.json()['response']['data'])

    data_return['area'] = area

    return(data_return)

def fetch_energy_consumption(eia_key: str, destdir: str):

    petro_mn = consumption_query("PMTCB", "MN", eia_key)
    imports_mn = consumption_query("ELNIB", "MN", eia_key)
    coal_mn = consumption_query("CLTCB", "MN", eia_key)
    net_interstate_mn = consumption_query("ELISB", "MN", eia_key)
    renewables_mn = consumption_query("RETCB", "MN", eia_key)
    gas_mn = consumption_query("NNTCB", "MN", eia_key)
    nuclear_mn = consumption_query("NUETB", "MN", eia_key)
    total_mn = consumption_query("TETCB", "MN", eia_key)

    petro_us = consumption_query("PMTCB", "US", eia_key)
    imports_us = consumption_query("ELNIB", "US", eia_key)
    coal_us = consumption_query("CLTCB", "US", eia_key)
    net_interstate_us = consumption_query("ELISB", "US", eia_key)
    renewables_us = consumption_query("RETCB", "US", eia_key)
    gas_us = consumption_query("NNTCB", "US", eia_key)
    nuclear_us = consumption_query("NUETB", "US", eia_key)
    total_us = consumption_query("TETCB", "US", eia_key)

    # subset total and rename value
    total_mn_subset = total_mn[["period", "value", "area"]]
    total_us_subset = total_us[["period", "value", "area"]]

    total_subset = pd.concat([total_mn_subset, total_us_subset])

    total_subset = total_subset.rename(columns={"value": "total_consumption"})

    # Append tables together
    consumption = pd.concat(
        [petro_mn, imports_mn, coal_mn, net_interstate_mn, renewables_mn, gas_mn, nuclear_mn, total_mn,
         petro_us, imports_us, coal_us, net_interstate_us, renewables_us, gas_us, nuclear_us, total_us],
        ignore_index=True)

    consumption = consumption.merge(total_subset, on = ["period", "area"])
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

    # Create labels for line graphs
    max_year = consumption['period'].max()

    consumption['percent_label'] = consumption.apply(

        lambda x: f"{round(x['percent'] * 100, 1)}%"
        if x['period'] == max_year
        else None,
        axis=1

    )

    consumption['total_label'] = consumption.apply(

        lambda x: x['value']
        if x['period'] == max_year
        else None,
        axis = 1

    )

    # Include column with 25% consumption for renewable consumption goal

    # get total consumption for MN in the max year in the dataset
    top_year = consumption.loc[(consumption['period'] == max_year) & (consumption['stateId'] == "MN"), [
        'total_consumption']].drop_duplicates().reset_index(drop=True).iloc[0]

    # calculate the 25% figure

    consumption['renewable_goal'] = consumption.apply(

        lambda x: top_year * .25
        if x['stateId'] == 'MN'
        else None,
        axis=1

    )

    consumption.to_csv(destdir + "/total_energy_consumption.csv", index = False)


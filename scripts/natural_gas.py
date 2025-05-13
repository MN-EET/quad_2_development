import pandas as pd
from requests import get

def fetch_henry_hub(eia_key: str, destdir: str):
    response =  get(
        "https://api.eia.gov/v2/natural-gas/pri/fut/data/?api_key=" + eia_key + "&frequency=monthly&data[0]=value&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000").json()

    henry_hub = pd.json_normalize(response['response']['data'])

    # subset data and convert columns
    cols_keep = ['period', 'value', 'units']

    henry_hub = henry_hub.loc[henry_hub['process-name'] == 'Spot Price', cols_keep]
    henry_hub['value'] = henry_hub['value'].astype(float)
    henry_hub['period'] = pd.to_datetime(henry_hub['period'], format='%Y-%m')

    # create label for chart
    max_period = henry_hub['period'].max()

    max_value = henry_hub.loc[henry_hub['period'] == max_period, 'value'].values[0]

    henry_hub['label'] = henry_hub['period'].map(lambda x: max_value if x == max_period else None)

    # write to csv
    henry_hub.to_csv(destdir + "/henry_hub.csv", index = False)
import pandas as pd
from requests import get
from datetime import datetime

def fetch_nuclear_facilities(eia_key: str, destdir: str):
    # query available facilities
    response = get("https://api.eia.gov/v2/electricity/operating-generator-capacity/data/?api_key=" +
                   eia_key +
                   "&frequency=monthly&data[0]=nameplate-capacity-mw&data[1]=operating-year-month&data[2]=planned-retirement-year-month&facets[technology][]=Nuclear&facets[status][]=OP&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000").json()

    nuclear_facilities = pd.json_normalize(response['response']['data'])

    # change column types and subset
    nuclear_facilities['period'] = pd.to_datetime(nuclear_facilities['period'], format='%Y-%m')
    nuclear_facilities['nameplate-capacity-mw'] = nuclear_facilities['nameplate-capacity-mw'].astype('float')
    nuclear_facilities['planned-retirement-year-month'] = pd.to_datetime(
        nuclear_facilities['planned-retirement-year-month'], format='%Y-%m')
    nuclear_facilities['operating-year-month'] = pd.to_datetime(nuclear_facilities['operating-year-month'],
                                                                format='%Y-%m')
    nuclear_facilities['open_year'] = nuclear_facilities['operating-year-month'].dt.year
    nuclear_facilities = nuclear_facilities.loc[
        nuclear_facilities['period'] == max(nuclear_facilities['period']), ['plantName', 'balancing-authority-name',
                                                                            'nameplate-capacity-mw',
                                                                            'operating-year-month', 'open_year',
                                                                            'stateName']]

    # write file
    nuclear_facilities.to_csv(destdir + "/nuclear_facilities.csv", index = False)
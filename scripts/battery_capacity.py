import pandas as pd
from requests import get
from datetime import datetime
import numpy as np

def fetch_battery_capacity(eia_key: str, destdir: str):
    # define max year for dataset
    report_year = datetime.now().year - 1

    # Define urls to query
    mn_path = "https://api.eia.gov/v2/electricity/operating-generator-capacity/data/?api_key=" + eia_key + "&frequency=monthly&data[0]=nameplate-capacity-mw&data[1]=operating-year-month&facets[technology][]=Batteries&facets[status][]=OP&facets[stateid][]=MN&start=2024-11&end=2024-12&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"
    miso_path = "https://api.eia.gov/v2/electricity/operating-generator-capacity/data/?api_key=" + eia_key + "&frequency=monthly&data[0]=nameplate-capacity-mw&data[1]=operating-year-month&facets[balancing_authority_code][]=MISO&facets[technology][]=Batteries&facets[status][]=OP&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000"

    # Define function to fetch and transform data from paths
    def fetch_region_battery(path: str, area_name: str):
        response = get(path).json()
        batteries = pd.json_normalize(response['response']['data'])
        batteries['period'] = pd.to_datetime(batteries['period'], format='%Y-%m')
        batteries['open_year'] = pd.to_datetime(batteries['operating-year-month'], format='%Y-%m').dt.year
        batteries['nameplate-capacity-mw'] = batteries['nameplate-capacity-mw'].astype('float')
        batteries['area_name'] = area_name
        batteries = batteries.loc[
            (batteries['period'] == max(batteries['period'])) & (batteries['open_year'] <= report_year), ['area_name',
                                                                                                          'nameplate-capacity-mw',
                                                                                                          'open_year']]
        batteries = batteries.groupby(['area_name', 'open_year'], as_index=False).sum(
            'nameplate-capacity-mw').sort_values('open_year')
        batteries['cumulative_capacity'] = batteries['nameplate-capacity-mw'].cumsum()
        batteries['total_label'] = np.where(batteries['open_year'] == batteries['open_year'].max(),
                                            batteries['cumulative_capacity'], pd.NA)
        return batteries

    # Fetch MN and MISO data and concatenate them
    mn_batteries = fetch_region_battery(mn_path, "Minnesota")
    miso_batteries = fetch_region_battery(miso_path, "MISO")
    total_batteries = pd.concat([mn_batteries, miso_batteries])


    total_batteries.to_csv(destdir + "/battery_capacity.csv", index = False)
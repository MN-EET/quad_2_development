import pandas as pd
from requests import get
from datetime import datetime

def fetch_miso_annual(eia_key: str, destdir: str):

    area = "MN"

    area_label = "Minnesota"

    query_year = str(datetime.now().year - 1)

    # create dictionaries to label dataset
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    def fetch_data(fuel_type):
        q1_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key
            + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]="
            + fuel_type + "&start=" + query_year + "-01-01T00&end=" + query_year
            + "-03-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
        ).json()
        q2_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key
            + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]="
            + fuel_type + "&start=" + query_year + "-04-01T00&end=" + query_year
            + "-06-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
        ).json()
        q3_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key
            + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]="
            + fuel_type + "&start=" + query_year + "-07-01T00&end=" + query_year
            + "-09-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
        ).json()
        q4_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key
            + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]="
            + fuel_type + "&start=" + query_year + "-10-01T00&end=" + query_year
            + "-12-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
        ).json()

        q1_data = pd.json_normalize(q1_response['response']['data'])
        q2_data = pd.json_normalize(q2_response['response']['data'])
        q3_data = pd.json_normalize(q3_response['response']['data'])
        q4_data = pd.json_normalize(q4_response['response']['data'])

        # bind rows together
        hourly_gen = pd.concat([q1_data, q2_data, q3_data, q4_data], ignore_index=True)

        # convert column types
        hourly_gen['period'] = pd.to_datetime(hourly_gen['period'], format='%Y-%m-%dT%H', utc=True)
        hourly_gen['month'] = hourly_gen['period'].dt.month
        hourly_gen['period'] = hourly_gen['period'].dt.tz_convert('America/Chicago')
        hourly_gen['hour_label'] = hourly_gen['period'].dt.strftime('%#I:00 %p')
        hourly_gen['year'] = hourly_gen['period'].dt.year
        hourly_gen['hour'] = hourly_gen['period'].dt.hour
        hourly_gen['value'] = hourly_gen['value'].fillna(0).astype(int)

        # map labels
        hourly_gen['month_name'] = hourly_gen['month'].map(month_names)

        hourly_gen = hourly_gen[['period', 'value', 'month_name', 'month', 'hour',
                                 'year', 'hour_label', 'type-name']]

        return hourly_gen

    # fetch data by fuel type and combine
    nuclear = fetch_data('NUC')
    # battery = fetch_data('BAT')  # Not available for 2024 but is available starting in 2025
    coal = fetch_data('COL')
    natural_gas = fetch_data('NG')
    # oil = fetch_data('OIL')
    other = fetch_data('OTH')
    solar = fetch_data('SUN')
    hydro = fetch_data('WAT')
    wind = fetch_data('WND')


    hourly_gen = pd.concat([nuclear, coal, natural_gas, other, solar, hydro, wind])

    # aggregate monthly and annual averages
    year_gen = hourly_gen.groupby(['type-name', 'hour_label', 'hour'], as_index=False).mean('value')
    year_gen['month_name'] = 'Annual'
    year_gen['month'] = 0
    monthly_gen = hourly_gen.groupby(['type-name', 'month_name', 'month',
                                      'hour_label', 'hour'], as_index=False).mean('value')

    # Combine monthly and annual data
    gen_hourly = pd.concat([monthly_gen, year_gen], axis=0)

    # Aggregate and write
    gen_annual = gen_hourly.groupby('type-name', as_index=False)['value'].sum('value')
    gen_annual['total_generation'] = gen_annual['value'].sum()
    gen_annual['percent_generation'] = gen_annual['value'] / gen_annual['total_generation']

    gen_annual.to_csv(destdir + "/miso_annual_generation.csv", index = False)


import pandas as pd
from requests import get
from datetime import datetime

def fetch_miso_hourly(eia_key: str, destdir: str):
    # retrieve past year
    query_year = str(datetime.now().year - 1)

    # create dictionaries to label dataset
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    # hours from EIA are in UTC
    hour_labels = {
    0:  '7:00 PM',  1:  '8:00 PM',  2:  '9:00 PM',  3: '10:00 PM',
    4: '11:00 PM',  5: '12:00 AM',  6:  '1:00 AM',  7:  '2:00 AM',
    8:  '3:00 AM',  9:  '4:00 AM', 10:  '5:00 AM', 11:  '6:00 AM',
   12:  '7:00 AM', 13:  '8:00 AM', 14:  '9:00 AM', 15: '10:00 AM',
   16: '11:00 AM', 17: '12:00 PM', 18:  '1:00 PM', 19:  '2:00 PM',
   20:  '3:00 PM', 21:  '4:00 PM', 22:  '5:00 PM', 23:  '6:00 PM'}

    # define fetch data function

    def fetch_data(fuel_type):
        q1_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]=" + fuel_type + "&start=" + query_year + "-01-01T00&end=" + query_year + "-03-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000").json()
        q2_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]=" + fuel_type + "&start=" + query_year + "-04-01T00&end=" + query_year + "-06-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000").json()
        q3_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]=" + fuel_type + "&start=" + query_year + "-07-01T00&end=" + query_year + "-09-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000").json()
        q4_response = get(
            "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[fueltype][]=" + fuel_type + "&start=" + query_year + "-10-01T00&end=" + query_year + "-12-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000").json()

        q1_data = pd.json_normalize(q1_response['response']['data'])
        q2_data = pd.json_normalize(q2_response['response']['data'])
        q3_data = pd.json_normalize(q3_response['response']['data'])
        q4_data = pd.json_normalize(q4_response['response']['data'])

        # bind rows together
        hourly_gen = pd.concat([q1_data, q2_data, q3_data, q4_data], ignore_index=True)

        # convert column types
        hourly_gen['period'] = pd.to_datetime(hourly_gen['period'], format='%Y-%m-%dT%H')
        hourly_gen['month'] = hourly_gen['period'].dt.month
        hourly_gen['hour'] = hourly_gen['period'].dt.hour
        hourly_gen['year'] = hourly_gen['period'].dt.year
        hourly_gen['value'] = hourly_gen['value'].fillna(0).astype(int)

        # map labels
        hourly_gen['month_name'] = hourly_gen['month'].map(month_names)
        hourly_gen['hour_labels'] = hourly_gen['hour'].map(hour_labels)

        hourly_gen = hourly_gen[['period', 'value', 'month_name', 'month', 'hour', 'year', 'hour_labels', 'type-name']]

        return hourly_gen

    # fetch data by fuel type and combine
    nuclear = fetch_data('NUC')
    # battery = fetch_data('BAT') Not available for 2024 but is available starting in 2025
    coal = fetch_data('COL')
    natural_gas = fetch_data('NG')
    # oil = fetch_data('OIL')
    other = fetch_data('OTH')
    solar = fetch_data('SUN')
    hydro = fetch_data('WAT')
    wind = fetch_data('WND')

    hourly_gen = pd.concat([nuclear, coal, natural_gas, other, solar, hydro, wind])

    # fetch data by fuel type and combine
    nuclear = fetch_data('NUC')
    # battery = fetch_data('BAT') Not available for 2024 but is available starting in 2025
    coal = fetch_data('COL')
    natural_gas = fetch_data('NG')
    # oil = fetch_data('OIL')
    other = fetch_data('OTH')
    solar = fetch_data('SUN')
    hydro = fetch_data('WAT')
    wind = fetch_data('WND')

    hourly_gen = pd.concat([nuclear, coal, natural_gas, other, solar, hydro, wind])

    # aggregate monthly and annual averages
    year_gen = hourly_gen.groupby(['type-name', 'hour', 'hour_labels'], as_index=False).mean('value')
    year_gen['month_name'] = 'Annual'
    year_gen['month'] = 0
    monthly_gen = hourly_gen.groupby(['type-name', 'month_name', 'month', 'hour', 'hour_labels'], as_index=False).mean('value')

    # Combine monthly and annual data
    gen_hourly = pd.concat([monthly_gen, year_gen], axis=0)


    # write to csv
    gen_hourly.to_csv(destdir + "/miso_hourly_generation.csv", index = False)


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
        hourly_gen['period'] = pd.to_datetime(hourly_gen['period'], format='%Y-%m-%dT%H', utc=True)
        hourly_gen['month'] = hourly_gen['period'].dt.month
        hourly_gen['period'] = hourly_gen['period'].dt.tz_convert('America/Chicago')
        hourly_gen['hour_label'] = hourly_gen['period'].dt.strftime('%#I:00 %p')
        hourly_gen['year'] = hourly_gen['period'].dt.year
        hourly_gen['hour'] = hourly_gen['period'].dt.hour
        hourly_gen['value'] = hourly_gen['value'].fillna(0).astype(int)

        # map labels
        hourly_gen['month_name'] = hourly_gen['month'].map(month_names)

        hourly_gen = hourly_gen[['period', 'value', 'month_name', 'month', 'hour', 'year', 'hour_label', 'type-name']]

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

    hourly_gen = pd.concat([nuclear, coal , natural_gas, other, solar, hydro, wind])

    # aggregate monthly and annual averages
    year_gen = hourly_gen.groupby(['type-name', 'hour_label', 'hour'], as_index=False).mean('value')
    year_gen['month_name'] = 'Annual'
    year_gen['month'] = 0
    monthly_gen = hourly_gen.groupby(['type-name', 'month_name', 'month', 'hour_label', 'hour'], as_index=False).mean('value')

    # Combine monthly and annual data
    gen_hourly = pd.concat([monthly_gen, year_gen], axis=0)

    # Define function to pull hourly demand at MISO level

    def get_demand(url):
        raw_response = get(url).json()
        raw_demand = pd.json_normalize(raw_response['response']['data'])

        # convert period to datetime and convert hours to central time
        raw_demand['period'] = pd.to_datetime(raw_demand['period'], format='%Y-%m-%dT%H', utc=True)
        raw_demand['month'] = raw_demand['period'].dt.month
        raw_demand['period'] = raw_demand['period'].dt.tz_convert('America/Chicago')
        raw_demand['hour_label'] = raw_demand['period'].dt.strftime('%#I:00 %p')

        # convert mwh to int
        raw_demand['demand_mwh'] = raw_demand['value'].fillna(0).astype(int)

        # aggregate by hour
        # raw_demand = raw_demand.groupby(['month', 'hour_label'], as_index = False).agg({"demand_mwh": "mean"})

        return raw_demand

    # define urls to query
    jan_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-01-01T00&end=" + query_year + "-01-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    feb_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-02-01T00&end=" + query_year + "-02-28T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    mar_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-03-01T00&end=" + query_year + "-03-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    apr_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-04-01T00&end=" + query_year + "-04-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    may_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-05-01T00&end=" + query_year + "-05-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    jun_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-06-01T00&end=" + query_year + "-06-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    jul_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-07-01T00&end=" + query_year + "-07-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    aug_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-08-01T00&end=" + query_year + "-08-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    sep_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-09-01T00&end=" + query_year + "-09-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    oct_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-10-01T00&end=" + query_year + "-10-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    nov_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-11-01T00&end=" + query_year + "-11-30T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    dec_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=" + eia_key + "&frequency=hourly&data[0]=value&facets[respondent][]=MISO&facets[type][]=D&start=" + query_year + "-12-01T00&end=" + query_year + "-12-31T00&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000"
    # Query and combine for total demand

    total_demand = pd.concat([get_demand(jan_url),
                              get_demand(feb_url),
                              get_demand(mar_url),
                              get_demand(apr_url),
                              get_demand(may_url),
                              get_demand(jun_url),
                              get_demand(jul_url),
                              get_demand(aug_url),
                              get_demand(sep_url),
                              get_demand(oct_url),
                              get_demand(nov_url),
                              get_demand(dec_url)])

    # Aggregate annual demand by hour
    annual_demand = total_demand.groupby(['hour_label'], as_index=False).mean('demand_mwh')
    annual_demand['month_name'] = "Annual"

    # Aggregate total demand to find average hourly demand by month
    total_demand['month_name'] = total_demand['month'].map(month_names)
    total_demand = total_demand.groupby(['month_name', 'hour_label'], as_index=False).mean('demand_mwh')

    # combine average annual and monthly demand by hour
    combined_demand = pd.concat([annual_demand, total_demand])
    combined_demand = combined_demand[['hour_label', 'month_name', 'demand_mwh']]

    # join with average hourly generation by source and fine percent of demand met by source
    gen_hourly = pd.merge(gen_hourly, combined_demand, on=['hour_label', 'month_name'])
    gen_hourly['percent_demand_met'] = gen_hourly['value'] / gen_hourly['demand_mwh']

    # write to csv
    gen_hourly.to_csv(destdir + "/miso_hourly_generation.csv", index = False)


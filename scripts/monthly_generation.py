import pandas as pd
from requests import get

def fetch_monthly_gen(eia_key: str, destdir: str):

    # query EIA for monthly coal generation data in Minnesota
    response = get("https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?api_key=" + eia_key +"&frequency=monthly&data[0]=generation&facets[location][]=MN&facets[sectorid][]=99&facets[fueltypeid][]=ALL&facets[fueltypeid][]=AOR&facets[fueltypeid][]=BIO&facets[fueltypeid][]=COW&facets[fueltypeid][]=HYC&facets[fueltypeid][]=NG&facets[fueltypeid][]=SUN&facets[fueltypeid][]=WND&facets[fueltypeid][]=NUC&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000").json()
    gen_data = pd.json_normalize(response['response']['data'])

    # convert column types
    gen_data['generation'] = gen_data['generation'].astype(float)
    gen_data['period'] = pd.to_datetime(gen_data['period'], format='%Y-%m')

    # subset hydro electric values and add them to all renewables

    hydro_values = gen_data.loc[
        gen_data['fuelTypeDescription'] == 'conventional hydroelectric', ['period', 'generation']].rename(
        columns={'generation': 'hydro_gen'}).set_index('period')

    # map hydro values to all renewables and add them in
    gen_data.loc[gen_data['fuelTypeDescription'] == 'all renewables', 'generation'] += (
        gen_data.loc[gen_data['fuelTypeDescription'] == 'all renewables', 'period'].map(hydro_values['hydro_gen'])
    )

    gen_data = gen_data[['period', 'fuelTypeDescription', 'generation']]

    gen_data.to_csv(destdir + '/monthly_electricity_generation.csv', index=False)
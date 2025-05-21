import pandas as pd
import requests

def fetch_miso_queue(destdir):
    url = "https://www.misoenergy.org/api/giqueue/getprojects"
    response = requests.get(url)
    data = response.json()
    miso_queue = pd.DataFrame(data)

    # Fix incorrect state abbreviation
    def fix_state(state):
        if state == 'Michigan':
            return 'MI'
        elif state == 'AK':
            return 'AR'
        else:
            return state

    miso_queue['state'] = miso_queue['state'].map(lambda x: fix_state(x))

    # Change column types and subset
    miso_queue['queueDate'] = pd.to_datetime(miso_queue['queueDate'])
    miso_queue['inService'] = pd.to_datetime(miso_queue['inService'])
    miso_queue['queue_year'] = miso_queue['queueDate'].dt.year
    miso_queue['service_year'] = miso_queue['inService']
    miso_queue = miso_queue.loc[:,
                 ['queueDate', 'county', 'state', 'studyCycle', 'summerNetMW', 'winterNetMW', 'applicationStatus',
                  'fuelType', 'facilityType', 'service_year', 'queue_year']]

    miso_queue.to_csv(destdir + "/miso_queue.csv", index = False)
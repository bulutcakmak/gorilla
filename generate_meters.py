import numpy as np
import pandas as pd

def generate_meters(number_of_meters):

  # Let's first define all possible exit zones
  # we can use some global variables, or load the rate table, but to ensure we don't
  # rely on any external information, for now we will hardcode the possibilities
  
  zones = ['EA1','EA2','EA3','EA4','EM1','EM2','EM3','EM4',
           'LC','LO','LS','LT','LW',
           'NE1','NE2','NE3','NO1','NO2','NT1','NT2','NT3','NW1','NW2',
           'SC1','SC2','SC4','SE1','SE2','SO1','SO2','SW1','SW2','SW3',
           'WA1','WA2','WM1','WM2','WM3']

  # If we want to avoid hardcoding, we could use the snippet below:
  # url = 'https://github.com/bulutcakmak/gorilla/blob/main/gorilla_test_data.xlsx?raw=true'
  # zones = pd.unique(pd.ExcelFile(url).parse(2)['exit_zone'])
  
  # first generate meter_id as random 8-digit number
  # for randomness, we will now need to use numpy as well because pandas relies
  # on this library's random functions

  meter_id = np.random.randint(low = 10**7, high = 10**8, size = number_of_meters)

  # then generate AQ values between 0 and 732000+73200

  aq_kwh = np.random.rand(number_of_meters) * (732000 + 73200)

  # then generate random Exit Zones for each meter

  exit_zone = np.random.choice(zones, size = number_of_meters)

  return pd.DataFrame(data={'meter_id': meter_id,
                            'aq_kwh': aq_kwh,
                            'exit_zone': exit_zone})

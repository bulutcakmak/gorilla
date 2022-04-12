import pandas as pd

def calculate_transportcost(meterList, forecastTable):

  url = 'https://github.com/bulutcakmak/gorilla/blob/main/gorilla_test_data.xlsx?raw=true'
  xls = pd.ExcelFile(url)
  rateTable = xls.parse(2)

  masterData = pd.merge(forecastTable, meterList, on = 'meter_id')
  masterData = pd.merge(masterData, rateTable, on = 'exit_zone', how = 'left', suffixes = ('_forecast', '_rate'))

  masterData = masterData[masterData['date_forecast'] >= masterData['date_rate']]
  masterData = masterData[masterData['aq_min_kwh'] <= masterData['aq_kwh']]
  masterData = masterData[masterData['aq_kwh'] < masterData['aq_max_kwh'].fillna(masterData['aq_kwh'].max()+1)]
  masterData = masterData.reset_index(drop = True)

  idx = masterData.groupby(['meter_id', 'date_forecast'])['date_rate'].transform(max) == masterData['date_rate']
  masterData = masterData[idx]

  masterData['cost'] = masterData['kwh'] * masterData['rate_p_per_kwh']

  # Don't forget to divide the cost by 100 to convert from pennies to pounds
  
  return pd.DataFrame({'Total_est_consumption': masterData.groupby('meter_id')['kwh'].sum(),
                       'Total_cost': masterData.groupby('meter_id')['cost'].sum()/100})

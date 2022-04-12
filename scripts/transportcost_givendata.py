import pandas as pd

url = 'https://github.com/bulutcakmak/gorilla/blob/main/gorilla_test_data.xlsx?raw=true'
xls = pd.ExcelFile(url)

# instead of hardcoding sheetnames, we will allow some flexibility by using
# sheet numbers however we will assume the sheet order is always meter list,
# forecast table, and then rate table

meterList = xls.parse(0)
forecastTable = xls.parse(1)
rateTable = xls.parse(2)

masterData = pd.merge(forecastTable, meterList, on = 'meter_id')

# Need to use a left join when dealing with rate because initially there will
# be multiple rates applicable to 1 forecast record

masterData = pd.merge(masterData, rateTable, on = 'exit_zone', how = 'left', suffixes = ('_forecast', '_rate'))

# Keep only the rates which apply to the forecast based on AQ of the meter

masterData = masterData[masterData['aq_min_kwh'] <= masterData['aq_kwh']]
masterData = masterData[masterData['aq_kwh'] < masterData['aq_max_kwh'].fillna(masterData['aq_kwh'].max()+1)]

# Any rate that is determined later than the forecast can already be discarded

masterData = masterData[masterData['date_forecast'] >= masterData['date_rate']]

# Reset indices before moving on

# masterData = masterData.reset_index(drop = True)

# Keep only the most recent rate that was determined before the forecast date

idx = masterData.groupby(['meter_id', 'date_forecast'])['date_rate'].transform(max) == masterData['date_rate']
masterData = masterData[idx]

# It's easy to compute the cost in-memory, so create a new field and add the
# total cost for the forecasted consumption in this new field

masterData['cost'] = masterData['kwh'] * masterData['rate_p_per_kwh']

print(masterData.groupby('meter_id')['kwh'].sum())
print(masterData.groupby('meter_id')['cost'].sum()/100)

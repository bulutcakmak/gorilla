# Gorilla - Python Case

First, let's load all the libraries we absolutely need.

```python
import pandas as pd
```

Then, let's make sure we are able to read the Excel file. I have placed the Excel file to a public repository on GitHub, so we will load the file from that URL. This way, we will ensure the script can be run from any location, terminal, driver, etc.

```python
url = 'https://github.com/bulutcakmak/gorilla/blob/main/gorilla_test_data.xlsx?raw=true'
xls = pd.ExcelFile(url)
```

Once the file is ready, we can read it into pandas

```python
# instead of hardcoding sheetnames, we will allow some flexibility by using
# sheet numbers however we will assume the sheet order is always meter list,
# forecast table, and then rate table

meterList = xls.parse(0)
forecastTable = xls.parse(1)
rateTable = xls.parse(2)
```

To make our analyses easier, we will merge the corresponding meter and rate information to every forecast record. At first, we will explode in size since Rate won't match Forecast 1:1 and then we will quickly filter to keep only the relevant rate information in the table.

```python
masterData = pd.merge(forecastTable, meterList, on = 'meter_id')

# Need to use a left join when dealing with rate because initially there will
# be multiple rates applicable to 1 forecast record

masterData = pd.merge(masterData, rateTable, on = 'exit_zone', how = 'left', suffixes = ('_forecast', '_rate'))
```

We did a left join, so we need to clean the dataset now (we need to choose the correct rate whose 1) date applies to the forecast date, and 2) AQ range includes AQ coming from the meter information)

```python
# Keep only the rates which apply to the forecast based on AQ of the meter

masterData = masterData[masterData['aq_min_kwh'] <= masterData['aq_kwh']]
masterData = masterData[masterData['aq_kwh'] < masterData['aq_max_kwh'].fillna(masterData['aq_kwh'].max()+1)]

# Any rate that is determined later than the forecast can already be discarded

masterData = masterData[masterData['date_forecast'] >= masterData['date_rate']]

# Keep only the most recent rate that was determined before the forecast date

idx = masterData.groupby(['meter_id', 'date_forecast'])['date_rate'].transform(max) == masterData['date_rate']
masterData = masterData[idx]
```

Now that we have picked the appropriate rates for each forecast, we can easily compute the total estimated consumption and total cost

```python
# It's easy to compute the cost in-memory, so create a new field and add the
# total cost for the forecasted consumption in this new field

masterData['cost'] = masterData['kwh'] * masterData['rate_p_per_kwh']

print(masterData.groupby('meter_id')['kwh'].sum())
print(masterData.groupby('meter_id')['cost'].sum()/100)
```

The results of running the script above can be summarized below:

<center>

Meter ID | Total Estimated Consumption (kWh) | Total Cost (£) 
---------|-----------------------------------|----------------
14676236 | 28978 | 100.152
34509937 | 78324 | 275.489
50264822 | 265667 | 731.244
88357331 | 484399 | 1433.160

</center>

Now let's write the function to generate random meters. Looking at the Meters from the Excel file, the meter ID will be a random 8-digit number. Exit zone will be chosen randomly from what's available in the Rate information. AQ will be randomly generated between 0 and 732000+73200 to make sure normal distribution in the three different AQ intervals.

```python
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
```

Now let's write the function to generate forecast data

```python
import numpy as np
import pandas as pd

def generate_consumption(meter_list, start_date, number_of_forecast):
  # the expected date input is DD-MM-YYYY
  if not (start_date.isdigit() and len(start_date) == 8):
    print('The function expects a start date in the YYYYMMDD string format')
    return -1

  # replicate date and meter lists to prepare for forecast data

  forecast = pd.concat([
                       pd.DataFrame(
                           {'meter_id': row['meter_id'],
                            'date': pd.date_range(start = start_date, periods = number_of_forecast)
                            }
                          ) for i, row in meter_list.iterrows()
                        ], ignore_index=True)

  # The forecast table has the following for kwh field
  # Max: 1169.40
  # Min: 2.92
  # Mean: 251.28
  # Median: 137.60
  # So I will generate random consumption data uniformly over 0 to 600
  # This doesn't reflect the median and excludes the maximum, but it will be close
  # to the mean value

  forecast['kwh'] = np.random.rand(len(forecast)) * 600

  return forecast
```

Now let's write a function that will take a meter list and consumption forecast table and will calculate transportation cost table

```python
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

  return pd.DataFrame({'Total_est_consumption': masterData.groupby('meter_id')['kwh'].sum(),
                       'Total_cost': masterData.groupby('meter_id')['cost'].sum()/100})
```

We can include the script for benchmark testing here as well

```python
import time

meter_size = 10
date_size = 10
myDate = '20200401'
myFactorOfTesting = 100

# Create a matrix of zeroes
# The rows will represent the runtime w.r.t. number of meters
# The columns will represent the runtime w.r.t. number of forecast days

time_data = np.zeros((meter_size, date_size))

for num_meters in np.arange(meter_size):
  for num_days in np.arange(date_size):
    myMeters = generate_meters(myFactorOfTesting * (num_meters + 1))
    myForecast = generate_consumption(myMeters, myDate, myFactorOfTesting * (num_days + 1))
    start = time.time()
    myCost = calculate_transportcost(myMeters, myForecast)
    end = time.time()
    time_data[num_meters, num_days] = end - start

print(time_data)
```

<center>

Runtime | 1 day | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10
-|------------|------------|------------|------------|------------|------------|------------|------------|------------|-----------
1 meter | 0.59596395 | 0.59631014 | 0.65174961 | 0.71879435 | 0.79435015 | 0.84070921 | 0.91539121 | 1.08901262 | 1.06490564 | 1.15191483
2 | 0.59782147 | 0.70206261 | 0.8248868  | 0.9494791  | 1.09390569 | 1.22909617 | 1.33497882 | 1.48677063 | 1.62023973 | 1.74147487
3 | 0.63890147 | 0.89842415 | 1.04814768 | 1.20009899 | 1.35628915 | 1.52551556 | 1.69939899 | 1.91143656 | 2.77823162 | 2.37577605
4 | 0.69177508 | 0.95658875 | 1.15000272 | 1.3795743  | 1.61753488 | 1.84194446 | 2.13940024 | 2.35948586 | 2.75161242 | 3.15899682
5 | 0.76924229 | 1.08683491 | 1.39722633 | 1.61931133 | 1.95037293 | 2.22859645 | 2.5715251  | 2.92439246 | 3.17735553 | 3.63098311
6 | 0.8600049  | 1.1702981  | 1.48872447 | 1.83426046 | 2.17515969 | 2.55643344 | 2.93993878 | 3.26307535 | 3.69937038 | 4.30548906
7 | 1.05325294 | 1.31611967 | 1.71979904 | 2.09067225 | 2.57886195 | 2.86918449 | 3.4012177  | 3.82565427 | 4.19577885 | 4.8689537
8 | 1.21188402 | 1.39476991 | 1.85262418 | 2.34930134 | 2.73641205 | 3.22245955 | 3.76958179 | 4.23481655 | 4.6781311  | 5.56383967
9 | 1.0979929  | 1.50825787 | 2.04069591 | 2.52720928 | 3.00106072 | 3.59504056 | 4.14525461 | 4.67854071 | 5.36094117 | 6.1320591
10 | 1.07020593 | 1.67674255 | 2.17802405 | 2.70821667 | 3.39020872 | 3.89539528 | 4.56565523 | 5.19666362 | 5.76374936 | 6.28406501

</center>

In terms of time performance, I don't think this code is close to perfect. We see that, if we fix either of the axes, the increase in time isn't necessarily uniform. For example, if we were to check how runtime increases with each forecast day for a fixed number of meters, we see that the result is very different when we have 1 meter vs 10 meters. However, it is notable that every (i,j)-th element where i > j takes longer than (j,i)-th element. For example, 10 days of forecast with 9 meters takes longer than 9 days with 10 meters, so the burden of increasing the forecast horizon is (understandably) heavier on the code. This makes sense as for every new forecasting day introduced a new category to be grouped by at the ```idx``` variable of the ```calculate_transportcost``` function. Therefore, I would first concentrate on improving how to choose the matching rate.

The rest of the code is pretty standardized, and I can't see a better way to replace the ```merge``` function without using SQL, which is beyond the requirements of the case. Currently, the strategy is to explode the merged table in memory by creating a new record for each possible rate given the exit zone, but that could be replaced with a smarter way to either create a temporary table to be filled with only the correct rate at each row, or picking the rate one-by-one. For now, for readability and convenience reasons, I have opted to stick to the groupby solution. As is, the scripts would run into memory issues before runtime errors since the explosion will increase drastically as our time horizon expands -- we can reasonably assume that companies will want to forecast much longer than 10 days -- so that logic should probably be altered in a real implementation.

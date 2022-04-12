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

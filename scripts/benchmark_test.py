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

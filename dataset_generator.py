import pandas as pd
import numpy as np

def generate_price(dt):
    hour = dt.hour
    month = dt.month
    base = 0.10
    if month in [6, 7, 8, 12, 1, 2]:
        seasonal_multiplier = 1.2
    else:
        seasonal_multiplier = 1.0
    if hour in [7, 8, 9, 17, 18, 19, 20, 21]:
        peak_offpeak_multiplier = 1.5
    else:
        peak_offpeak_multiplier = 0.8
    price = base * seasonal_multiplier * peak_offpeak_multiplier + np.random.normal(0, 0.01)
    return max(price, 0)

def generate_load(dt):
    hour = dt.hour
    base_load = 5.0  # kW
    if 18 <= hour < 22:
        multiplier = 1.5
    elif 0 <= hour < 6:
        multiplier = 0.5
    else:
        multiplier = 1.0
    load = base_load * multiplier + np.random.normal(0, 0.5)
    return max(load, 0)

# Generate hourly dates for January 2023 (for testing)
dates = pd.date_range(start='2023-01-01', end='2023-01-31 23:00:00', freq='h')
regions = ['North', 'South', 'East', 'West']
data = []

for region in regions:
    prices = [generate_price(dt) for dt in dates]
    loads = [generate_load(dt) for dt in dates]
    df = pd.DataFrame({'datetime': dates, 'region': region, 'price': prices, 'load': loads})
    data.append(df)

dataset = pd.concat(data, ignore_index=True)
dataset.to_csv('C:/Users/abhij/OneDrive/Desktop/IEMS MiniProject/v2/sample_battery_data.csv', index=False)
print("Sample dataset saved to 'C:/Users/abhij/OneDrive/Desktop/IEMS MiniProject/v2/sample_battery_data.csv'.")
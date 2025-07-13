import pandas as pd
import numpy as np

CAPACITY = 10.0  # kWh
P_MAX = 5.0  # kW
ETA = 0.9  # Efficiency
INITIAL_SOC = 5.0  # kWh

def optimize_battery(df):
    results = []
    for region, group in df.groupby('region'):
        group = group.sort_values('datetime')
        prices = group['price'].values
        loads = group['load'].values
        datetimes = group['datetime'].values
        T = len(prices)
        SOC = INITIAL_SOC
        for t in range(T):
            if t >= 24:
                forecast = prices[t-24:t]
            else:
                forecast = prices[0:24]
            threshold = np.mean(forecast)
            price_t = prices[t]
            load_t = loads[t]
            if price_t < threshold and SOC < CAPACITY:
                charge_power = min(P_MAX, (CAPACITY - SOC) / ETA)
                discharge_power = 0.0
                SOC_new = min(CAPACITY, SOC + charge_power * ETA)
                action = 'charge'
            elif price_t > threshold and SOC > 0:
                discharge_power = min(P_MAX, load_t, SOC * ETA)
                charge_power = 0.0
                SOC_new = max(0, SOC - discharge_power / ETA)
                action = 'discharge'
            else:
                charge_power = 0.0
                discharge_power = 0.0
                SOC_new = SOC
                action = 'idle'
            results.append({
                'datetime': datetimes[t],
                'region': region,
                'price': price_t,
                'load': load_t,
                'threshold': threshold,
                'action': action,
                'SOC': SOC_new,
                'charge_power': charge_power,
                'discharge_power': discharge_power
            })
            SOC = SOC_new
    return pd.DataFrame(results)
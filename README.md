BATTERY STORAGE OPTIMIZATION WITH DYNAMIC PRICING
==================================================

PROJECT DESCRIPTION
-------------------
This project focuses on optimizing battery storage operations in response to dynamic electricity pricing, 
aiming to minimize grid energy costs and simulate smart energy usage. By integrating mathematical 
optimization, synthetic data generation, and machine learning, the system simulates real-world pricing 
scenarios and determines the best times to charge or discharge a battery for cost efficiency.

OBJECTIVES
----------
- Minimize electricity cost from the grid using a battery.
- Use optimization and forecasting to plan energy usage.
- Apply machine learning for real-time action prediction.
- Provide a user-friendly dashboard for data visualization and interaction.

HOW IT WORKS
------------
1. Synthetic Dataset Generation:
   - Fields: datetime, price, region, demand
   - Simulates hourly electricity prices over a year
   - Accounts for seasonal, hourly, and random variations

2. Perfect Foresight Optimization:
   - Assumes complete knowledge of future prices
   - Uses linear programming to compute optimal charge/discharge schedule
   - Serves as ground truth for model training

3. Model Predictive Control (MPC):
   - Uses recent historical prices to forecast next 24 hours
   - Solves LP iteratively with updated forecasts
   - Reflects real-world adaptive behavior

4. Machine Learning-Based Prediction:
   - Trains a Random Forest Classifier
   - Input features: hour, dayofweek, month, price, state of charge (SoC)
   - Target: charge / discharge / idle
   - Used to provide quick predictions based on current conditions

5. Interactive Dashboard (Dash + Plotly):
   - Allows users to pick date & time to check predicted battery status
   - Displays optimal action, predicted action, and battery state
   - Graphs: Price over time, Demand, SoC, Battery Action
   - Visualizes total cost savings from battery usage

FEATURES
--------
- Linear programming for optimization (Pulp)
- Random Forest classifier for action prediction
- Model Predictive Control with naive forecasting
- Fully interactive web dashboard with visualizations
- Synthetic CSV dataset used for training and evaluation
- Supports hourly data, full-year simulation

USE CASES
---------
- Residential solar/battery optimization
- Smart grid energy simulations
- Cost-effective energy storage planning
- AI-powered battery control demonstrations
- Educational tool for optimization and ML in energy


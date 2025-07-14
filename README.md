# 🔋 Battery Storage Optimization using Dynamic Pricing

## 📌 Overview
This project demonstrates a smart battery storage optimization system driven by dynamic electricity pricing. It aims to minimize energy costs by intelligently scheduling battery charge and discharge actions. The system uses a combination of **mathematical optimization (Linear Programming)**, **predictive control (MPC)**, and **machine learning** to make efficient decisions in real-time.

It features a fully interactive **web dashboard** where users can:
- Upload datasets (synthetic or real)
- Visualize battery behavior
- Monitor electricity prices and actions
- Choose parameters for real-time predictions

---

##  How It Works

### 1. Dataset
Synthetic CSV files (like `syn25.csv` or `syn26.csv`) are generated using `dataset_generator.py` and contain:
- `datetime`: hourly timestamps
- `price`: dynamic electricity price ($/kWh)
- `region`: region label (e.g., North)
- `demand`: user load in kWh

### 2. Optimization Strategies

- **Perfect Foresight Optimization** 
  - Assumes future prices are fully known.
  - Solves using **Linear Programming (PuLP)**.
  - Provides baseline optimal solution.

- **Model Predictive Control (MPC)**
  - Forecasts future prices using historical data.
  - Re-optimizes decisions every hour.
  - Mimics real-world predictive behavior.

- **Machine Learning Model**
  - Trained using **Random Forest Classifier**.
  - Predicts actions: `charge`, `discharge`, `idle`.
  - Features used: `hour`, `dayofweek`, `month`, `price`, `SoC`.

---

## Core Formula

### State of Charge (SoC) Update Rule:
SoC(t+1) = SoC(t) + η_charge * Charge(t) - Discharge(t) / η_discharge

### Objective:
Minimize total cost:
Σ (Load + Charge - Discharge) × Price

Constraints include:
- SoC bounds (0 ≤ SoC ≤ capacity)
- Max charge/discharge rates
- Initial SoC set to 0

---

## ⚙️ Technologies Used

| Component               | Tech Used                        |
|------------------------|----------------------------------|
| Frontend               | Dash (Plotly), Tailwind CSS      |
| Backend                | Python, Flask (Dash Base)        |
| Optimization           | PuLP (Linear Programming)        |
| Machine Learning       | Scikit-learn (Random Forest)     |
| Data Handling          | Pandas, NumPy                    |
| Visualization          | Plotly Express, Plotly Graphs    |

---

## 💡 App Screenshots

### 🔹 1. Startup Interface (Before File Upload)
![Startup](1.png)

---

### 🔹 2. Main Analytics Page
- Price vs Time
- Demand vs Time
- Battery SoC over Time
- Action plot (Charge/Discharge/Idle)

![Analytics](2.png)

---

### 🔹 3. Control Panel: Parameter & Date Selection
- Select a date and time
- See if battery is charging
- Compare ML prediction vs optimal behavior

![Parameter Selection](3.png)

---

## 🚀 Running the App

1. **Generate Data**  
   ```bash
   python dataset_generator.py
   ```
2. **Start Dashboard**
   ```bash
   streamlit run app.py
   ```
The dashboard will open in your default browser.

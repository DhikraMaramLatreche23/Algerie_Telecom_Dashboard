# 📡 Algeria Telecom — Intelligent Data-Driven Forecasting Dashboard

> **Design and Development of an Intelligent Data-Driven Web Application for Forecasting and Decision Support**

A data science and AI internship project developed at **Algérie Télécom – Annaba** as part of the academic program at the **National Higher School of Artificial Intelligence (ENSIA)**, Sidi Abdallah, Algiers.

---

## 👩‍💻 Contributors

| Name | Institution |
|---|---|
| **Dhikra Maram LATRECHE** | ENSIA – National Higher School of Artificial Intelligence |
| **Hadjer BORDJIBA** | ENSIA – National Higher School of Artificial Intelligence |

**Supervisor:** Med Amir LAKNAOUI  
**Host Company:** Algérie Télécom – Annaba  
**Date:** September 2025

---

## 🌐 Live Application

🔗 [https://algerietelecom-analysis-dashboard.streamlit.app/](https://algerietelecom-analysis-dashboard.streamlit.app/)

---

## 📌 Project Overview

Algérie Télécom frequently faces challenges in planning infrastructure transitions — for example, migrating from **ADSL to FTTH (Fiber to the Home)** — and historically relies on rough estimations for equipment procurement. Since FTTH infrastructure is imported (mainly from China), poor estimates lead to costly over-purchasing or service-delaying under-purchasing.

This project addresses that problem by building an **intelligent, interactive forecasting system** that:

- Analyzes historical telecom data across Internet, Mobile, and Fixed Line services
- Applies multiple time-series forecasting models to predict future demand
- Presents results through an intuitive Streamlit dashboard accessible to non-technical managers

---

## 🎯 Objectives

- Replace random estimation with **evidence-based demand forecasting**
- Provide interactive dashboards with real-time scenario testing
- Support strategic planning for technology transitions (ADSL → FTTH, GSM → 4G/5G)
- Enable managers to enter new data, explore trends, and generate reports — without technical expertise

---

## 📊 Data Sources & Coverage

Data was collected from Algérie Télécom internal records and **ARPCE** (Autorité de Régulation de la Poste et des Communications Électroniques), covering three service domains:

| Domain | Period | Key Metrics |
|---|---|---|
| **Internet** | Q4 2018 – Q1 2025 | Subscriber base (ADSL, FTTH, LTE, 3G/4G), traffic, ARPU |
| **Mobile** | Q1 2019 – Q1 2025 | GSM/3G/4G subscribers per operator (Mobilis, Djezzy, Ooredoo), prepaid/postpaid split |
| **Fixed Line** | Q1 2019 – Q1 2025 | On-net/off-net traffic, minutes per subscriber, incoming/outgoing calls |

---

## 🤖 Forecasting Models

The following models were trained, evaluated, and compared for each service domain:

- **Prophet** — strong interpretability for trends and seasonality
- **SARIMAX** — seasonal autoregressive integrated moving average with exogenous variables
- **XGBoost** — captures non-linear growth patterns
- **LSTM Neural Network** — deep learning for complex time-series sequences
- **ARIMA** — classical time-series baseline
- **Exponential Smoothing** — smoothed trend projection
- **Linear Regression** — simple directional baseline

Models were evaluated using **MAE**, **RMSE**, and **R² Score**.

---

## 📈 Key Results

### Internet Services
| Metric | 2025 Value | 2027 Forecast | Best Model |
|---|---|---|---|
| Total Internet Subscribers | 58.1M | 65.9M (+13.4%) | XGBoost |
| FTTH Subscribers | 1.93M | 1.96M (+1.5%) | LSTM |
| Total Data Traffic | 1.36T units | 1.71T units (+25.1%) | LSTM |
| 4G Mobile Subscribers | 47.8M | 57.8M (+21.0%) | LSTM |

### Mobile Services
- GSM (2G) declining across all operators → 3G/4G migration ongoing
- Prepaid remains dominant; 4G adoption continues to rise
- 5G planning recommended to sustain future service quality

### Fixed Line Services
- Fixed Internet growing modestly, driven by FTTH
- Fixed voice traffic (on-net, off-net, incoming, outgoing) declining sharply
- Mobile-first behavior and VoIP apps are the main drivers of fixed-line decline

---

## 🛠️ Tech Stack

| Category | Tools / Libraries |
|---|---|
| **Language** | Python 3.11 |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Seaborn, Matplotlib |
| **Forecasting** | Prophet, Statsmodels (ARIMA/SARIMAX/Exp. Smoothing), Scikit-learn, XGBoost |
| **Dashboard** | Streamlit |
| **Version Control** | GitHub |

---

## 🖥️ Application Features

The deployed Streamlit app is structured around three user roles:

### 1. 📥 Enter New Value
Update the dataset with new quarterly data for any service metric. The interface shows recent historical values so the user can validate their entry before saving.

### 2. 🔍 Analyze Previous Years
Explore historical trends through:
- Comparative analysis across technologies (ADSL vs FTTH vs LTE)
- Anomaly detection
- Correlation matrices
- Growth rate and moving average charts
- Report & CSV export

### 3. 📅 Forecast Coming Years
Select a service domain, metric, and set of forecasting models. The system will:
- Train and compare all selected models automatically
- Generate forecasts with confidence intervals
- Display error analysis (residuals, heatmaps, actual vs predicted)
- Export results as CSV or Excel

---

## 🗂️ Project Structure

```
algerie-telecom-dashboard/
│
├── app.py                    # Main Streamlit entry point
├── pages/
│   ├── home.py               # Landing page
│   ├── select_role.py        # Role selection page
│   ├── enter_new_value.py    # Data entry page
│   ├── analyze_previous.py   # Historical analysis page
│   └── forecast_coming.py    # Forecasting page
│
├── data/
│   ├── internet_data.csv
│   ├── mobile_data.csv
│   └── fixed_data.csv
│
├── models/
│   └── forecasting_utils.py  # Model training, evaluation, comparison
│
├── requirements.txt
└── README.md
```

> **Note:** Adjust the structure above to match your actual repository layout.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/algerie-telecom-dashboard.git
cd algerie-telecom-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Requirements

```
streamlit
pandas
numpy
plotly
matplotlib
seaborn
prophet
scikit-learn
statsmodels
xgboost
```

---

## 💡 Business Impact

This system enabled Algérie Télécom to:

- **Anticipate demand** for fiber, mobile, and bandwidth resources
- **Optimize procurement** and reduce costs tied to over/under-purchasing of imported equipment
- **Plan infrastructure investments** (FTTH rollout, 4G/5G capacity upgrades)
- **Support national broadband strategy** and digital transformation goals
- **Generate structured reports** accessible to managers without a technical background

---

## 🔭 Recommendations for Future Work

1. **Live Database Integration** — Automate data updates directly from Algérie Télécom's internal systems
2. **Hybrid Models** — Explore LSTM + Prophet combinations for improved non-linear accuracy
3. **Geographic Forecasting** — Extend analysis to regional/wilaya-level granularity
4. **BI Integration** — Connect with Power BI or Tableau for richer enterprise reporting
5. **User Training** — Organize workshops for managers to maximize dashboard adoption

---

## 🙏 Acknowledgments

Special thanks to **Mr. Mohammed Amir Laknaoui** for his guidance and continuous support throughout the internship, to the staff of **Algérie Télécom – Annaba** for their warm welcome and cooperation, and to **ENSIA** for providing the academic foundation that made this project possible.

---

## 📄 License

This project was developed as part of an academic internship program at ENSIA. All data belongs to Algérie Télécom and ARPCE. Please contact the contributors for any reuse inquiries.

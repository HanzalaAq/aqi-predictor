# 🌍 AQI Predictor - Karachi Air Quality Forecasting System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-yellow.svg)](https://github.com/HanzalaAq/aqi-predictor/actions)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-brightgreen.svg)](https://www.mongodb.com)

> **End-to-end ML system predicting Air Quality Index for Karachi, Pakistan with 6% error rate**

A fully automated, serverless machine learning pipeline that forecasts Air Quality Index (AQI) for the next 3 days. The system achieves 94% accuracy and operates entirely on free-tier cloud services.

[🔗 Live Dashboard](#) | [📊 View Report](./reports/Final_Report.md) | [🐛 Report Issues](https://github.com/HanzalaAq/aqi-predictor/issues)

---

## ✨ Key Features

- **🎯 Accurate Predictions**: 6% error rate (4.15 AQI points) validated against real-time data
- **⚡ Real-time Updates**: Hourly automated data collection and predictions
- **🤖 Multi-Model System**: Trains Random Forest, XGBoost, and LightGBM; selects best performer
- **🔄 Fully Automated**: GitHub Actions CI/CD for feature engineering, training, and inference
- **📊 Interactive Dashboard**: Streamlit web app with health alerts and 3-day forecasts
- **💾 Cloud Infrastructure**: MongoDB Atlas for feature store and model registry
- **🔍 Explainable AI**: SHAP analysis for feature importance visualization
- **💰 Zero Cost**: Runs entirely on free-tier services

---

## 🏗️ Architecture

```
┌──────────────┐
│ Open-Meteo   │  Air quality & weather data (free API)
│     API      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│        Feature Pipeline (hourly)         │
│  • Fetch current data                    │
│  • Engineer 41 features                  │
│  • Store in MongoDB                      │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│   MongoDB Atlas (Feature Store)          │
│  • 5,904 training samples                │
│  • 41 engineered features                │
└──────┬───────────────────────────────────┘
       │
       ├──────────────────┬─────────────────┐
       ▼                  ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Random    │  │   XGBoost   │  │  LightGBM   │
│   Forest    │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
       │                  │                 │
       └──────────────────┴─────────────────┘
                     │
                     ▼
           ┌──────────────────┐
           │  Model Registry  │
           │   (MongoDB)      │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Inference Engine │
           │ (72h forecast)   │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │    Streamlit     │
           │    Dashboard     │
           └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (free tier)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/HanzalaAq/aqi-predictor.git
cd aqi-predictor
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB URI
```

5. **Run initial setup**
```bash
# Backfill historical data (one-time, ~5 minutes)
python backfill_to_mongodb.py

# Train models
python src/pipelines/training_pipeline.py

# Generate predictions
python src/pipelines/inference_pipeline.py
```

6. **Launch dashboard**
```bash
streamlit run app/streamlit_app.py
```

Visit http://localhost:8501 to see your dashboard!

---

## 📁 Project Structure

```
aqi-predictor/
├── .github/
│   └── workflows/           # CI/CD automation
│       ├── feature_pipeline.yml
│       ├── training_pipeline.yml
│       └── inference_pipeline.yml
├── src/
│   ├── data/
│   │   ├── fetch_data.py          # API integration
│   │   └── feature_engineering.py  # Feature creation
│   ├── models/
│   │   └── train.py               # Model training
│   ├── storage/
│   │   ├── mongodb_client.py      # Database connection
│   │   ├── feature_store.py       # Feature storage
│   │   └── model_registry.py      # Model versioning
│   ├── pipelines/
│   │   ├── feature_pipeline.py
│   │   ├── training_pipeline.py
│   │   └── inference_pipeline.py
│   └── utils/
│       └── config.py              # Configuration
├── app/
│   └── streamlit_app.py           # Web dashboard
├── notebooks/
│   └── eda_analysis.ipynb         # Exploratory analysis
├── data/                          # Local data (gitignored)
├── models/                        # Saved models
├── reports/
│   ├── Final_Report.md            # Complete documentation
│   └── feature_importance.png     # SHAP analysis
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=aqi_features
MODEL_DATABASE=aqi_models
PREDICTION_DATABASE=aqi_predictions

# Location Configuration
LATITUDE=24.8607
LONGITUDE=67.0011
CITY_NAME=Karachi
```

### GitHub Secrets (for CI/CD)

Add these secrets in repository Settings → Secrets:
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `MODEL_DATABASE`
- `PREDICTION_DATABASE`

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **Prediction Error** | 6% (4.15 AQI points) |
| **R² Score** | 0.99 |
| **Training Samples** | 5,904 hourly records |
| **Features** | 41 (engineered from 13 raw) |
| **Update Frequency** | Every hour |
| **Forecast Horizon** | 72 hours (3 days) |

### Feature Importance (SHAP)

Top 5 predictive features:
1. `pm2_5_rolling_3h` - 30.55
2. `aqi_rolling_3h` - 15.91
3. `ozone` - 4.68
4. `aqi_change_rate` - 3.18
5. `aqi_lag_1h` - 2.91

---

## 🤖 Automation

### GitHub Actions Workflows

- **Feature Pipeline**: Runs every hour at :10
  - Fetches latest air quality data
  - Engineers features
  - Stores in MongoDB

- **Training Pipeline**: Runs daily at 2:00 AM
  - Trains 3 models
  - Evaluates performance
  - Updates model registry

- **Inference Pipeline**: Runs every hour at :30
  - Loads best model
  - Generates 72-hour forecast
  - Updates dashboard

---

## 🎨 Dashboard Features

- **Current AQI Display**: Real-time air quality status
- **Health Alerts**: 
  - 🚨 Hazardous (AQI ≥ 151)
  - ⚠️ Unhealthy (AQI 101-150)
  - ✅ Good (AQI ≤ 50)
- **3-Day Forecast Chart**: Interactive visualization
- **Hourly Predictions**: Detailed 72-hour table
- **Model Information**: Current model and metrics
- **Manual Refresh**: Update data on demand

---

## 🧪 Testing

Run tests:
```bash
# Test MongoDB connection
python test_mongodb.py

# Test data pipeline
python test_pipeline_no_db.py

# Test feature engineering
python src/data/feature_engineering.py

# Validate predictions
python validate_predictions.py
```

---

## 📈 Results & Validation

**Case Study: January 25, 2026**
- Predicted AQI: 71
- Actual AQI: 69.74
- Error: 1.8% ✅

System consistently achieves <10% error, outperforming typical forecasting services (10-15% error).

---

## 🐛 Known Issues & Solutions

### 1. MongoDB SSL Handshake Error
**Solution**: Implemented in `mongodb_client.py`
```python
tlsCAFile=certifi.where()
tlsAllowInvalidCertificates=True
```

### 2. Stale Dashboard Data
**Solution**: Added manual refresh button
```python
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()
```



---

## 🛠️ Technologies Used

- **ML/Data**: Scikit-learn, XGBoost, LightGBM, Pandas, NumPy
- **Explainability**: SHAP
- **Database**: MongoDB Atlas
- **API**: Open-Meteo (air quality & weather)
- **CI/CD**: GitHub Actions
- **Dashboard**: Streamlit, Plotly
- **Deployment**: Streamlit Cloud

---

## 📝 Future Enhancements

- [ ] Multi-city support (Lahore, Islamabad, Multan)
- [ ] Email/SMS alerts for hazardous conditions
- [ ] Deep learning models (LSTM, Transformers)
- [ ] Mobile app (React Native)
- [ ] Historical accuracy tracking
- [ ] Ensemble methods for improved accuracy
- [ ] Additional data sources (traffic, industrial activity)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

---

## 👨‍💻 Author

**Muhammad Hanzala Afaq**

- GitHub: [@HanzalaAq](https://github.com/HanzalaAq)
- Email: realhanzala56@gmail.com
- LinkedIn: [Hanzala Afaq](https://www.linkedin.com/in/muhammad-hanzala-afaq-3993b1257/)

---

## 🙏 Acknowledgments

- Open-Meteo for free air quality API
- MongoDB Atlas for cloud database
- Streamlit for dashboard framework
- GitHub Actions for CI/CD infrastructure
- US EPA for AQI calculation standards

---

## 📊 Project Stats

![GitHub last commit](https://img.shields.io/github/last-commit/HanzalaAq/aqi-predictor)
![GitHub code size](https://img.shields.io/github/languages/code-size/HanzalaAq/aqi-predictor)
![Lines of code](https://img.shields.io/tokei/lines/github/HanzalaAq/aqi-predictor)

---

**⭐ If you find this project useful, please consider giving it a star!**

---

*Built with ❤️ for cleaner air in Karachi*      

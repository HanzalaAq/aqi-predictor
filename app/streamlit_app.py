import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.storage.mongodb_client import mongodb_client
from src.utils.config import Config
from src.data.fetch_data import fetch_latest_data

# Page configuration
st.set_page_config(
    page_title="AQI Predictor - Karachi",
    page_icon="🌍",
    layout="wide"
)

st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1rem;
}
.current-box {
    background-color: #e3f2fd;
    border-left: 5px solid #2196F3;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
.prediction-box {
    background-color: #fff3e0;
    border-left: 5px solid #FF9800;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🌍 Air Quality Index Predictor</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem;">Real-Time & 3-Day AQI Forecast for Karachi</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Dashboard Info")
st.sidebar.info(
    "🔵 **Current AQI** - Real-time actual air quality\n\n"
    "🟠 **Predictions** - ML forecast for next 3 days"
)

st.sidebar.header("🔍 AQI Categories")
st.sidebar.markdown("""
- 0-50: Good 🟢
- 51-100: Moderate 🟡
- 101-150: Unhealthy for Sensitive 🟠
- 151-200: Unhealthy 🔴
- 201-300: Very Unhealthy 🟣
- 301+: Hazardous 🟤
""")

if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

# Helper functions
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "🟣"
    else:
        return "Hazardous", "🟤"

# Load current AQI
@st.cache_data(ttl=600)
def load_current_aqi():
    try:
        df = fetch_latest_data()
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Load predictions
@st.cache_data(ttl=600)
def load_predictions():
    try:
        pred_db = mongodb_client.get_prediction_store()
        pred_coll = pred_db[Config.PREDICTIONS_COLLECTION]
        
        preds = list(pred_coll.find().sort("timestamp", 1).limit(72))
        
        if preds:
            df = pd.DataFrame(preds)
            df = df.drop('_id', axis=1, errors='ignore')
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Only future predictions
            now = datetime.now()
            df = df[df['timestamp'] > now]
            
            return df
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# SECTION 1: CURRENT AQI
st.markdown('<div class="current-box">', unsafe_allow_html=True)
st.markdown("## 🔵 Current Air Quality (Real-Time)")

current_data = load_current_aqi()

if current_data is not None and not current_data.empty:
    current_aqi = current_data['aqi'].iloc[-1]
    current_time = current_data['timestamp'].iloc[-1]
    category, emoji = get_aqi_category(current_aqi)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current AQI", f"{current_aqi:.0f}")
    with col2:
        st.metric("Category", category)
    with col3:
        st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
    with col4:
        st.metric("As of", current_time.strftime('%H:%M'))
    
    st.markdown("**Today's Statistics:**")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Min", f"{current_data['aqi'].min():.0f}")
    with col_b:
        st.metric("Average", f"{current_data['aqi'].mean():.0f}")
    with col_c:
        st.metric("Max", f"{current_data['aqi'].max():.0f}")
else:
    st.warning("⚠️ Unable to fetch current AQI")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# SECTION 2: PREDICTIONS
st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
st.markdown("## 🟠 AI Predictions (Next 3 Days)")

predictions = load_predictions()

if predictions is not None and not predictions.empty:
    
    model_name = predictions.iloc[0].get('model_name', 'Unknown')
    created_at = predictions.iloc[0].get('created_at', datetime.now())
    
    st.info(f"🤖 Model: {model_name.upper()} | Generated: {created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Chart
    st.markdown("### 📈 72-Hour Forecast")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=predictions['timestamp'],
        y=predictions['predicted_aqi'],
        mode='lines+markers',
        name='Predicted AQI',
        line=dict(color='#FF9800', width=3)
    ))
    
    fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=50, y1=100, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=100, y1=150, fillcolor="orange", opacity=0.1, line_width=0)
    
    fig.update_layout(
        xaxis_title="Date & Time",
        yaxis_title="AQI",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Daily summary
    st.markdown("### 📋 Daily Summary")
    
    predictions['date'] = predictions['timestamp'].dt.date
    daily = predictions.groupby('date')['predicted_aqi'].agg(['min', 'max', 'mean']).round(0)
    daily = daily.reset_index().head(3)
    
    cols = st.columns(len(daily))
    for idx, row in daily.iterrows():
        with cols[idx]:
            day = pd.to_datetime(row['date']).strftime('%a %b %d')
            avg = row['mean']
            cat, emoji = get_aqi_category(avg)
            
            st.markdown(f"**{day}**")
            st.metric("Avg AQI", f"{avg:.0f}")
            st.markdown(f"<div style='text-align:center;font-size:2rem'>{emoji}</div>", unsafe_allow_html=True)
            st.caption(f"{row['min']:.0f} - {row['max']:.0f}")
    
    st.markdown("---")
    
    # Alerts
    st.markdown("### 🚨 Alerts")
    
    hazardous = predictions[predictions['predicted_aqi'] >= 151]
    unhealthy = predictions[(predictions['predicted_aqi'] >= 101) & (predictions['predicted_aqi'] < 151)]
    
    if len(hazardous) > 0:
        st.error(f"🚨 HAZARDOUS: {len(hazardous)} hours with AQI ≥ 151")
        st.error("• Stay indoors • Use air purifiers • Wear N95 masks")
    elif len(unhealthy) > 0:
        st.warning(f"⚠️ WARNING: {len(unhealthy)} hours with AQI 101-150")
        st.warning("• Sensitive groups limit outdoor activities")
    elif current_data is not None and current_data['aqi'].iloc[-1] <= 50:
        st.success("✅ GOOD air quality - Safe for all activities")
    else:
        st.info("ℹ️ MODERATE air quality - Acceptable for most")

else:
    st.warning("⚠️ No predictions available")
    st.info("Run: `python src/pipelines/inference_pipeline.py`")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="text-align:center;color:gray">Built with Streamlit & MongoDB | Open-Meteo API</p>', unsafe_allow_html=True)

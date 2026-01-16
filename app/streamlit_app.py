import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.storage.mongodb_client import mongodb_client
from src.storage.model_registry import model_registry
from src.utils.config import Config

# Page configuration
st.set_page_config(
    page_title="AQI Predictor - Karachi",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🌍 Air Quality Index Predictor</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem;">3-Day AQI Forecast for Karachi, Pakistan</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Dashboard Info")
st.sidebar.info(
    "This dashboard predicts the Air Quality Index (AQI) "
    "for Karachi for the next 3 days using machine learning models trained on historical data."
)

st.sidebar.header("🔍 About AQI")
st.sidebar.markdown("""
**AQI Categories:**
- 0-50: Good (Green)
- 51-100: Moderate (Yellow)
- 101-150: Unhealthy for Sensitive (Orange)
- 151-200: Unhealthy (Red)
- 201-300: Very Unhealthy (Purple)
- 301+: Hazardous (Maroon)
""")

# Helper functions
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "🟣"
    else:
        return "Hazardous", "🟤"

def get_aqi_color(aqi):
    if aqi <= 50:
        return "#00E400"
    elif aqi <= 100:
        return "#FFFF00"
    elif aqi <= 150:
        return "#FF7E00"
    elif aqi <= 200:
        return "#FF0000"
    elif aqi <= 300:
        return "#8F3F97"
    else:
        return "#7E0023"

# Load predictions
@st.cache_data(ttl=3600)
def load_predictions():
    try:
        prediction_db = mongodb_client.get_prediction_store()
        prediction_collection = prediction_db[Config.PREDICTIONS_COLLECTION]
        
        # Get latest predictions
        cursor = prediction_collection.find().sort("created_at", -1).limit(72)
        predictions = list(cursor)
        
        if predictions:
            df = pd.DataFrame(predictions)
            df = df.drop('_id', axis=1)
            df = df.sort_values('timestamp')
            return df
        return None
    except Exception as e:
        st.error(f"Error loading predictions: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_model_info():
    try:
        models = model_registry.list_models()
        return models
    except Exception as e:
        st.error(f"Error loading model info: {str(e)}")
        return []

# Main content
predictions = load_predictions()

if predictions is not None and not predictions.empty:
    
    # Current AQI metrics
    st.markdown("### 📍 Current AQI Status")
    col1, col2, col3, col4 = st.columns(4)
    
    current_aqi = predictions.iloc[0]['predicted_aqi']
    category, emoji = get_aqi_category(current_aqi)
    
    with col1:
        st.metric("Current AQI", f"{current_aqi:.0f}")
    
    with col2:
        st.metric("Air Quality", category)
    
    with col3:
        st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
    
    with col4:
        model_name = predictions.iloc[0]['model_name']
        st.metric("Model", model_name.upper())
    
    st.markdown("---")
    
    # 3-day forecast chart
    st.markdown("### 📅 3-Day AQI Forecast")
    
    fig = go.Figure()
    
    # Add AQI prediction line
    fig.add_trace(go.Scatter(
        x=predictions['timestamp'],
        y=predictions['predicted_aqi'],
        mode='lines+markers',
        name='Predicted AQI',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    # Add AQI category zones
    fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=50, y1=100, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=100, y1=150, fillcolor="orange", opacity=0.1, line_width=0)
    fig.add_hrect(y0=150, y1=200, fillcolor="red", opacity=0.1, line_width=0)
    fig.add_hrect(y0=200, y1=300, fillcolor="purple", opacity=0.1, line_width=0)
    
    fig.update_layout(
        title="AQI Forecast for Next 72 Hours",
        xaxis_title="Date & Time",
        yaxis_title="AQI Value",
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Daily summary
    st.markdown("### 📋 Daily AQI Summary")
    
    # Group by day
    predictions['date'] = pd.to_datetime(predictions['timestamp']).dt.date
    daily_summary = predictions.groupby('date').agg({
        'predicted_aqi': ['min', 'max', 'mean']
    }).round(2)
    
    daily_summary.columns = ['Min AQI', 'Max AQI', 'Avg AQI']
    daily_summary = daily_summary.reset_index()
    
    # Display as cards
    cols = st.columns(3)
    for idx, row in daily_summary.iterrows():
        with cols[idx]:
            st.markdown(f"**📅 {row['date']}**")
            st.metric("Average AQI", f"{row['Avg AQI']:.0f}")
            st.caption(f"Min: {row['Min AQI']:.0f} | Max: {row['Max AQI']:.0f}")
    
    st.markdown("---")
    
    # Detailed hourly forecast
    st.markdown("### 🕐 Hourly Forecast Details")
    
    display_df = predictions[['timestamp', 'predicted_aqi']].copy()
    display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
    display_df['predicted_aqi'] = display_df['predicted_aqi'].round(2)
    display_df['category'] = display_df['predicted_aqi'].apply(lambda x: get_aqi_category(x)[0])
    
    st.dataframe(
        display_df.rename(columns={
            'timestamp': 'Date & Time',
            'predicted_aqi': 'Predicted AQI',
            'category': 'Category'
        }),
        use_container_width=True,
        height=400
    )
    
    # Model information
    st.markdown("---")
    st.markdown("### 🤖 Model Information")
    
    models_info = load_model_info()
    if models_info:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Available Models:**")
            for model in models_info:
                st.write(f"- {model['_id']} (v{model['latest_version']})")
        
        with col2:
            st.markdown("**Last Updated:**")
            if models_info:
                last_update = models_info[0].get('created_at', 'Unknown')
                st.write(f"🕐 {last_update}")
    
else:
    st.warning("⚠️ No predictions available yet!")
    st.info("""
    **To generate predictions:**
    1. Run the feature pipeline to collect data
    2. Run the training pipeline to train models
    3. Run the inference pipeline to generate predictions
    
    Or wait for the automated pipelines to run (scheduled via GitHub Actions).
    """)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: gray;">Built with Streamlit & MongoDB | Data from Open-Meteo API</p>',
    unsafe_allow_html=True
)
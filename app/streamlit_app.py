# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime, timedelta
# import sys
# from pathlib import Path

# # Add src to path
# sys.path.append(str(Path(__file__).parent.parent))

# from src.storage.mongodb_client import mongodb_client
# from src.storage.model_registry import model_registry
# from src.utils.config import Config

# # Page configuration
# st.set_page_config(
#     page_title="AQI Predictor - Karachi",
#     page_icon="🌍",
#     layout="wide"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 3rem;
#         font-weight: bold;
#         text-align: center;
#         margin-bottom: 1rem;
#     }
#     .metric-card {
#         background-color: #f0f2f6;
#         padding: 20px;
#         border-radius: 10px;
#         text-align: center;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Title
# st.markdown('<div class="main-header">🌍 Air Quality Index Predictor</div>', unsafe_allow_html=True)
# st.markdown('<p style="text-align: center; font-size: 1.2rem;">3-Day AQI Forecast for Karachi, Pakistan</p>', unsafe_allow_html=True)

# # Sidebar
# st.sidebar.header("Dashboard Info")
# st.sidebar.info(
#     "This dashboard predicts the Air Quality Index (AQI) "
#     "for Karachi for the next 3 days using machine learning models trained on historical data."
# )

# # Show last refresh time
# st.sidebar.markdown("---")
# st.sidebar.markdown(f"**Last Refresh:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# st.sidebar.markdown("Dashboard updates automatically every hour")

# st.sidebar.markdown("---")
# st.sidebar.header("About AQI")
# st.sidebar.markdown("""
# **AQI Categories:**
# - 0-50: Good (Green)
# - 51-100: Moderate (Yellow)
# - 101-150: Unhealthy for Sensitive (Orange)
# - 151-200: Unhealthy (Red)
# - 201-300: Very Unhealthy (Purple)
# - 301+: Hazardous (Maroon)
# """)

# # Add manual refresh button
# if st.sidebar.button("Refresh Data"):
#     st.cache_data.clear()
#     st.rerun()

# # Helper functions
# def get_aqi_category(aqi):
#     if aqi <= 50:
#         return "Good", "🟢"
#     elif aqi <= 100:
#         return "Moderate", "🟡"
#     elif aqi <= 150:
#         return "Unhealthy for Sensitive Groups", "🟠"
#     elif aqi <= 200:
#         return "Unhealthy", "🔴"
#     elif aqi <= 300:
#         return "Very Unhealthy", "🟣"
#     else:
#         return "Hazardous", "🟤"

# def get_aqi_color(aqi):
#     if aqi <= 50:
#         return "#00E400"
#     elif aqi <= 100:
#         return "#FFFF00"
#     elif aqi <= 150:
#         return "#FF7E00"
#     elif aqi <= 200:
#         return "#FF0000"
#     elif aqi <= 300:
#         return "#8F3F97"
#     else:
#         return "#7E0023"

# # Load predictions
# @st.cache_data(ttl=3600)
# def load_predictions():
#     try:
#         prediction_db = mongodb_client.get_prediction_store()
#         prediction_collection = prediction_db[Config.PREDICTIONS_COLLECTION]
        
#         # Get latest predictions
#         cursor = prediction_collection.find().sort("created_at", -1).limit(72)
#         predictions = list(cursor)
        
#         if predictions:
#             df = pd.DataFrame(predictions)
#             df = df.drop('_id', axis=1)
#             df = df.sort_values('timestamp')
#             return df
#         return None
#     except Exception as e:
#         st.error(f"Error loading predictions: {str(e)}")
#         return None

# @st.cache_data(ttl=3600)
# def load_model_info():
#     try:
#         models = model_registry.list_models()
#         return models
#     except Exception as e:
#         st.error(f"Error loading model info: {str(e)}")
#         return []

# # Main content
# predictions = load_predictions()

# if predictions is not None and not predictions.empty:
    
#     # Current AQI metrics
#     st.markdown("### Current AQI Status")
#     col1, col2, col3, col4 = st.columns(4)
    
#     current_aqi = predictions.iloc[0]['predicted_aqi']
#     category, emoji = get_aqi_category(current_aqi)
    
#     with col1:
#         st.metric("Current AQI", f"{current_aqi:.0f}")
    
#     with col2:
#         st.metric("Air Quality", category)
    
#     with col3:
#         st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{emoji}</div>", unsafe_allow_html=True)
    
#     with col4:
#         model_name = predictions.iloc[0]['model_name']
#         st.metric("Model", model_name.upper())
    
#     # Show prediction generation time
#     pred_generated = predictions.iloc[0]['created_at']
#     st.caption(f"Predictions generated: {pd.to_datetime(pred_generated).strftime('%Y-%m-%d %H:%M:%S')}")
    
#     st.markdown("---")
        
#     st.markdown("### 🚨 Air Quality Alerts")
#     hazardous_predictions = predictions[predictions['predicted_aqi'] >= 151]
#     unhealthy_predictions = predictions[(predictions['predicted_aqi'] >= 101) & (predictions['predicted_aqi'] < 151)]
#     if len(hazardous_predictions) > 0:
#         st.error("🚨 **SEVERE AIR QUALITY ALERT!**")
#         st.error(f"🔴 {len(hazardous_predictions)} hours with dangerous AQI (≥151) predicted in next 3 days")
#         st.error("**Health Recommendations:**")
#         st.error("• Stay indoors with windows closed")
#         st.error("• Use air purifiers if available")
#         st.error("• Avoid all outdoor activities")
#         st.error("• Wear N95 masks if you must go outside")
#     elif len(unhealthy_predictions) > 0:
#         st.warning("⚠️ **AIR QUALITY WARNING**")
#         st.warning(f"🟠 {len(unhealthy_predictions)} hours with unhealthy AQI (101-150) predicted")
#         st.warning("**Health Recommendations:**")
#         st.warning("• Sensitive groups should limit outdoor activities")
#         st.warning("• Consider wearing masks outdoors")
#     elif current_aqi <= 50:
#         st.success("✅ **EXCELLENT AIR QUALITY**")
#         st.success("Air quality is ideal! Safe for all outdoor activities.")
#     elif current_aqi <= 100:
#         st.info("ℹ️ **MODERATE AIR QUALITY**")
#         st.info("Air quality is acceptable for most people.")
        
#     else:
#         st.info("📊 Air quality is within normal range.")
    
#     st.markdown("---")

#     st.markdown("### 3-Day AQI Forecast")
    
#     fig = go.Figure()
    
#     # Add AQI prediction line
#     fig.add_trace(go.Scatter(
#         x=predictions['timestamp'],
#         y=predictions['predicted_aqi'],
#         mode='lines+markers',
#         name='Predicted AQI',
#         line=dict(color='#FF6B6B', width=3),
#         marker=dict(size=8)
#     ))
    
#     # Add AQI category zones
#     fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, line_width=0)
#     fig.add_hrect(y0=50, y1=100, fillcolor="yellow", opacity=0.1, line_width=0)
#     fig.add_hrect(y0=100, y1=150, fillcolor="orange", opacity=0.1, line_width=0)
#     fig.add_hrect(y0=150, y1=200, fillcolor="red", opacity=0.1, line_width=0)
#     fig.add_hrect(y0=200, y1=300, fillcolor="purple", opacity=0.1, line_width=0)
    
#     fig.update_layout(
#         title="AQI Forecast for Next 72 Hours",
#         xaxis_title="Date & Time",
#         yaxis_title="AQI Value",
#         hovermode='x unified',
#         height=500,
#         showlegend=True
#     )
    
#     st.plotly_chart(fig, use_container_width=True)
    
#     # Daily summary
#     st.markdown("### Daily AQI Summary")
    
#     # Group by day
#     predictions['date'] = pd.to_datetime(predictions['timestamp']).dt.date
#     daily_summary = predictions.groupby('date').agg({
#         'predicted_aqi': ['min', 'max', 'mean']
#     }).round(2)
    
#     daily_summary.columns = ['Min AQI', 'Max AQI', 'Avg AQI']
#     daily_summary = daily_summary.reset_index()
    
#     # Display as cards
#     cols = st.columns(min(3, len(daily_summary)))
#     for idx, row in daily_summary.iterrows():
#         if idx < 3:
#             with cols[idx]:
#                 st.markdown(f"**{row['date']}**")
#                 st.metric("Average AQI", f"{row['Avg AQI']:.0f}")
#                 st.caption(f"Min: {row['Min AQI']:.0f} | Max: {row['Max AQI']:.0f}")
    
#     st.markdown("---")
    
#     st.markdown("### Hourly Forecast Details")
    
#     display_df = predictions[['timestamp', 'predicted_aqi']].copy()
#     display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
#     display_df['predicted_aqi'] = display_df['predicted_aqi'].round(2)
#     display_df['category'] = display_df['predicted_aqi'].apply(lambda x: get_aqi_category(x)[0])
    
#     st.dataframe(
#         display_df.rename(columns={
#             'timestamp': 'Date & Time',
#             'predicted_aqi': 'Predicted AQI',
#             'category': 'Category'
#         }),
#         use_container_width=True,
#         height=400
#     )
    
#     st.markdown("---")
#     st.markdown("### Model Information")
    
#     models_info = load_model_info()
#     if models_info:
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.markdown("**Available Models:**")
#             for model in models_info:
#                 st.write(f"- {model['_id']} (v{model['latest_version']})")
        
#         with col2:
#             st.markdown("**Model Training:**")
#             if models_info:
#                 last_update = models_info[0].get('created_at', 'Unknown')
#                 st.write(f"Last trained: {last_update}")
    
# else:
#     st.warning("No predictions available yet!")
#     st.info("""
#     **To generate predictions:**
#     1. Run the feature pipeline to collect data
#     2. Run the training pipeline to train models
#     3. Run the inference pipeline to generate predictions
    
#     Or wait for the automated pipelines to run (scheduled via GitHub Actions).
#     """)
    
#     # Show button to run inference manually
#     if st.button("Run Inference Pipeline Now"):
#         with st.spinner("Generating predictions..."):
#             try:
#                 import subprocess
#                 result = subprocess.run(
#                     ["python", "src/pipelines/inference_pipeline.py"],
#                     capture_output=True,
#                     text=True
#                 )
#                 if result.returncode == 0:
#                     st.success("Predictions generated successfully! Refresh the page.")
#                 else:
#                     st.error(f"Error: {result.stderr}")
#             except Exception as e:
#                 st.error(f"Error running pipeline: {str(e)}")

# # Footer
# st.markdown("---")
# st.markdown(
#     '<p style="text-align: center; color: gray;">Built with Streamlit & MongoDB | Data from Open-Meteo API</p>',
#     unsafe_allow_html=True
# )



import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
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

# Custom CSS
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
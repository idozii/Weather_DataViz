import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

from config import CITIES_BY_REGION, ALL_CITIES, DEFAULT_CITIES, REFRESH_OPTIONS
from utils import validate_api_key, fetch_weather, init_session_state
from ui_components import (
    render_header, render_country_buttons, render_weather_card,
    render_comparison_table, render_footer
)
import styles

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

#!PAGE CONFIGURATION
st.set_page_config(
    page_title="Weather Realtime Dashboard",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="expanded",
)

st.markdown(styles.hide_streamlit_elements(), unsafe_allow_html=True)
st.markdown(styles.get_custom_css(), unsafe_allow_html=True)

#!INITIALIZATION
init_session_state()

if "selected_region" not in st.session_state:
    st.session_state.selected_region = "All Cities"

if not validate_api_key(API_KEY):
    st.error("⚠️ Missing or invalid API key!")
    st.info("Please create a .env file with your OPENWEATHER_API_KEY.")
    st.code('OPENWEATHER_API_KEY=your_api_key_here', language='bash')
    st.stop()

#!HEADER
render_header()

#!SIDEBAR CONFIGURATION
st.sidebar.markdown("### ⚙️ Configuration")

#!Country selection buttons
render_country_buttons()

st.sidebar.divider()

#! Dropdown selector
st.sidebar.markdown("#### 📋 Or Use Dropdown")
selected_region_dropdown = st.sidebar.selectbox(
    "Choose a country",
    ["All Cities"] + list(CITIES_BY_REGION.keys()),
    index=0 if st.session_state.selected_region == "All Cities" else (
        list(CITIES_BY_REGION.keys()).index(st.session_state.selected_region) + 1
        if st.session_state.selected_region in CITIES_BY_REGION.keys() else 0
    ),
    label_visibility="collapsed"
)

if selected_region_dropdown != st.session_state.selected_region:
    st.session_state.selected_region = selected_region_dropdown

selected_region = st.session_state.selected_region
available_cities = CITIES_BY_REGION[selected_region] if selected_region != "All Cities" else ALL_CITIES

#! City selection
st.sidebar.markdown("#### 🏙️ Select Cities")
selected_cities = st.sidebar.multiselect(
    "Choose cities to monitor",
    options=available_cities,
    default=[c for c in DEFAULT_CITIES if c in available_cities][:3],
    label_visibility="collapsed"
)

#! Custom city input
st.sidebar.markdown("#### ➕ Add Custom City")
custom_city = st.sidebar.text_input(
    "City name (English)",
    placeholder="e.g., Amsterdam",
    label_visibility="collapsed"
)

if custom_city and custom_city.strip() and custom_city.strip() not in selected_cities:
    selected_cities.append(custom_city.strip())

st.sidebar.divider()

#! Display options
st.sidebar.markdown("### 📊 Display Options")
show_metrics = st.sidebar.checkbox("📋 Show detailed metrics", value=True)
show_comparison = st.sidebar.checkbox("📊 Show comparison table", value=False)

st.sidebar.divider()

#! Refresh settings
st.sidebar.markdown("### ⏱️ Refresh Settings")
selected_refresh = st.sidebar.selectbox(
    "Auto-refresh interval",
    options=list(REFRESH_OPTIONS.keys()),
    index=1,
    label_visibility="collapsed"
)

st_autorefresh(interval=REFRESH_OPTIONS[selected_refresh] * 1000, key="weather_autorefresh")

#! DATA FETCHING
if not selected_cities:
    st.warning("Please select at least one city to monitor.")
    st.stop()

current_data = []
with st.spinner("Fetching weather data..."):
    for city in selected_cities:
        record = fetch_weather(city, API_KEY, BASE_URL)
        if record:
            current_data.append(record)

if not current_data:
    st.warning("No data available. Please check your API key or city selection.")
    st.stop()

#! WEATHER DISPLAY
st.markdown("<h2 style='color: white; margin-top: 2rem; font-weight: 600; letter-spacing: -0.02em;'>📍 Current Weather</h2>", 
            unsafe_allow_html=True)

num_cols = min(4, max(1, len(current_data)))
cols = st.columns(num_cols, gap="medium")

for idx, record in enumerate(current_data):
    with cols[idx % len(cols)]:
        render_weather_card(record, show_metrics)

#! COMPARISON TABLE
if show_comparison and len(current_data) > 1:
    render_comparison_table(current_data)

#! FOOTER
render_footer()

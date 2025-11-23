import os
import time
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

CITIES_BY_REGION = {
    "🌏 Asia": ["Tokyo", "Seoul", "Beijing", "Shanghai", "Hong Kong", "Singapore", 
                "Bangkok", "Hanoi", "Ho Chi Minh", "Manila", "Jakarta", "Kuala Lumpur",
                "Mumbai", "Delhi", "Bangalore", "Dubai", "Istanbul"],
    "🌎 North America": ["New York", "Los Angeles", "Chicago", "Toronto", "Vancouver",
                         "Mexico City", "Miami", "San Francisco", "Seattle", "Boston"],
    "🌎 South America": ["São Paulo", "Rio de Janeiro", "Buenos Aires", "Lima", "Bogotá",
                         "Santiago", "Caracas", "Montevideo"],
    "🌍 Europe": ["London", "Paris", "Berlin", "Madrid", "Rome", "Amsterdam", "Vienna",
                  "Prague", "Warsaw", "Moscow", "Stockholm", "Oslo", "Copenhagen"],
    "🌍 Africa": ["Cairo", "Lagos", "Nairobi", "Johannesburg", "Cape Town", "Casablanca",
                  "Algiers", "Tunis"],
    "🌏 Oceania": ["Sydney", "Melbourne", "Brisbane", "Perth", "Auckland", "Wellington"]
}

# Flatten all cities for default dropdown
ALL_CITIES = [city for cities in CITIES_BY_REGION.values() for city in cities]
DEFAULT_CITIES = ["Sydney", "Tokyo", "London", "New York", "Paris"]

# Application settings
REFRESH_INTERVAL_MS = 60 * 1000  # 60 seconds
REQUEST_TIMEOUT = 10  # seconds
MAX_HISTORY_RECORDS = 200  # Maximum historical records per city
MAX_RETRIES = 2  # API request retry attempts

# Temperature thresholds for color coding
TEMP_COLD = 10
TEMP_COOL = 20
TEMP_WARM = 25
TEMP_HOT = 30


# ================== UTILITY FUNCTIONS ==================
def validate_api_key() -> bool:
    """
    Validate that API key is present and properly formatted.
    
    Returns:
        bool: True if API key is valid, False otherwise
    """
    if not API_KEY:
        return False
    if len(API_KEY) < 10:
        return False
    return True


def get_temp_emoji(temp: float) -> str:
    """Get emoji based on temperature."""
    if temp < TEMP_COLD:
        return "🥶"
    elif temp < TEMP_COOL:
        return "😊"
    elif temp < TEMP_WARM:
        return "☀️"
    elif temp < TEMP_HOT:
        return "🌡️"
    else:
        return "🔥"


def get_weather_icon(description: str) -> str:
    """Get weather icon based on description."""
    description = description.lower()
    if "clear" in description:
        return "☀️"
    elif "cloud" in description:
        return "☁️"
    elif "rain" in description or "drizzle" in description:
        return "🌧️"
    elif "thunder" in description or "storm" in description:
        return "⛈️"
    elif "snow" in description:
        return "❄️"
    elif "mist" in description or "fog" in description:
        return "🌫️"
    else:
        return "🌤️"


def get_temp_color(temp: float) -> str:
    """Get color code based on temperature."""
    if temp < TEMP_COLD:
        return "#3498db"  # Blue
    elif temp < TEMP_COOL:
        return "#2ecc71"  # Green
    elif temp < TEMP_WARM:
        return "#f39c12"  # Orange
    elif temp < TEMP_HOT:
        return "#e67e22"  # Dark orange
    else:
        return "#e74c3c"  # Red


# ================== DATA FETCHING ==================

def fetch_weather(city: str) -> Optional[Dict]:
    """
    Fetch weather data from OpenWeather API.
    
    Args:
        city: City name in English
        
    Returns:
        Dictionary containing weather information or None if error occurs
    """
    if not validate_api_key():
        st.error("Missing or invalid API key. Please set OPENWEATHER_API_KEY in .env file.")
        return None

    params = {
        "q": city.strip(),
        "appid": API_KEY,
        "units": "metric",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            # Validate response structure
            if "main" not in data or "weather" not in data:
                st.error(f"Invalid API response for {city}")
                return None

            main = data["main"]
            weather_desc = data["weather"][0]["description"].title()
            wind_speed = data.get("wind", {}).get("speed", 0)

            now_str = datetime.now().strftime("%H:%M:%S")

            return {
                "city": city,
                "time": now_str,
                "temp": main["temp"],
                "feels_like": main["feels_like"],
                "humidity": main["humidity"],
                "pressure": main["pressure"],
                "wind": wind_speed,
                "description": weather_desc,
            }
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                continue
            st.warning(f"Timeout fetching data for {city}. Please try again later.")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.error(f"❌ City '{city}' not found. Please check the spelling.")
            elif e.response.status_code == 401:
                st.error("❌ Invalid API key. Please wait 10-120 minutes for activation or check your key.")
            else:
                st.error(f"❌ HTTP error for {city}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Network error fetching data for {city}: {str(e)}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            st.error(f"Error parsing data for {city}: {str(e)}")
            return None
    
    return None


# ================== SESSION STATE MANAGEMENT ==================
def init_session_state():
    """Initialize session state variables."""
    if "history" not in st.session_state:
        # history: dict[city] = list[record]
        st.session_state.history = {}
    
    if "last_fetch_time" not in st.session_state:
        st.session_state.last_fetch_time = {}


def append_history(record: Dict) -> None:
    """
    Append weather record to history for a city.
    
    Args:
        record: Weather data dictionary
    """
    city = record["city"]
    if city not in st.session_state.history:
        st.session_state.history[city] = []
    st.session_state.history[city].append(record)

    # Limit records to prevent memory bloat
    if len(st.session_state.history[city]) > MAX_HISTORY_RECORDS:
        st.session_state.history[city] = st.session_state.history[city][-MAX_HISTORY_RECORDS:]


def get_history_df(city: str) -> pd.DataFrame:
    """
    Get historical weather data as DataFrame for a city.
    
    Args:
        city: City name
        
    Returns:
        DataFrame with time and temperature columns
    """
    records = st.session_state.history.get(city, [])
    if not records:
        return pd.DataFrame(columns=["time", "temp", "humidity", "pressure"])
    df = pd.DataFrame(records)
    return df[["time", "temp", "humidity", "pressure"]]


def clear_history(city: Optional[str] = None) -> None:
    """
    Clear history for a specific city or all cities.
    
    Args:
        city: City name to clear, or None to clear all
    """
    if city:
        st.session_state.history.pop(city, None)
    else:
        st.session_state.history = {}


# ================== UI ==================
st.set_page_config(
    page_title="Weather Realtime Dashboard",
    layout="wide",
    page_icon="🌤️",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    .weather-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2, h3 {
        color: white;
    }
    .stSelectbox label, .stMultiSelect label, .stCheckbox label {
        color: white !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Validate API key at startup
if not validate_api_key():
    st.error("⚠️ Missing or invalid API key!")
    st.info("Please create a .env file with your OPENWEATHER_API_KEY.")
    st.code('OPENWEATHER_API_KEY=your_api_key_here', language='bash')
    st.stop()

st.markdown("""
    <h1 style='text-align: center; font-size: 3.5rem; margin-bottom: 0;'>
        🌤️ Weather Realtime Dashboard
    </h1>
    <p style='text-align: center; color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 0;'>
        Real-time weather data with automatic updates and historical tracking
    </p>
""", unsafe_allow_html=True)

# Sidebar: configuration
st.sidebar.markdown("### ⚙️ Configuration")

# Region selector for easier city selection
st.sidebar.markdown("#### 🌍 Quick Select by Region")
selected_region = st.sidebar.selectbox(
    "Choose a region",
    ["All Cities"] + list(CITIES_BY_REGION.keys()),
    index=0,
    label_visibility="collapsed"
)

if selected_region != "All Cities":
    available_cities = CITIES_BY_REGION[selected_region]
else:
    available_cities = ALL_CITIES

st.sidebar.markdown("#### 🏙️ Select Cities")
selected_cities = st.sidebar.multiselect(
    "Choose cities to monitor",
    options=available_cities,
    default=[c for c in DEFAULT_CITIES if c in available_cities][:3],
    label_visibility="collapsed"
)

st.sidebar.markdown("#### ➕ Add Custom City")
custom_city = st.sidebar.text_input(
    "City name (English)",
    placeholder="e.g., Amsterdam",
    label_visibility="collapsed"
)

if custom_city:
    custom_city_clean = custom_city.strip()
    if custom_city_clean and custom_city_clean not in selected_cities:
        selected_cities.append(custom_city_clean)

st.sidebar.divider()

# Display settings
st.sidebar.markdown("### 📊 Display Options")
show_charts = st.sidebar.checkbox("📈 Show historical charts", value=True)
show_metrics = st.sidebar.checkbox("📋 Show detailed metrics", value=True)
show_comparison = st.sidebar.checkbox("📊 Show comparison table", value=False)

st.sidebar.divider()

# Refresh interval customization
st.sidebar.markdown("### ⏱️ Refresh Settings")
refresh_options = {"30 seconds": 30, "1 minute": 60, "2 minutes": 120, "5 minutes": 300}
selected_refresh = st.sidebar.selectbox(
    "Auto-refresh interval",
    options=list(refresh_options.keys()),
    index=1,
    label_visibility="collapsed"
)
actual_refresh_ms = refresh_options[selected_refresh] * 1000

# Auto-refresh with dynamic interval
st_autorefresh(interval=actual_refresh_ms, key="weather_autorefresh")

# Clear history button
if st.sidebar.button("🗑️ Clear All History"):
    clear_history()
    st.sidebar.success("History cleared!")

if not selected_cities:
    st.warning("Please select at least one city to monitor.")
    st.stop()


# Fetch current data for each city
current_data = []
with st.spinner("Fetching weather data..."):
    for city in selected_cities:
        record = fetch_weather(city)
        if record:
            current_data.append(record)
            append_history(record)

if not current_data:
    st.warning("No data available. Please check your API key or city selection.")
    st.stop()

# Display cards for each city
st.markdown("<h2 style='color: white; margin-top: 2rem;'>📍 Current Weather Overview</h2>", unsafe_allow_html=True)
num_cols = min(4, max(1, len(current_data)))  # Between 1 and 4 columns
cols = st.columns(num_cols, gap="medium")

for idx, record in enumerate(current_data):
    col = cols[idx % len(cols)]
    with col:
        # Calculate temperature delta if history exists
        temp_delta = None
        city_history = st.session_state.history.get(record['city'], [])
        if len(city_history) >= 2:
            prev_temp = city_history[-2]['temp']
            temp_delta = record['temp'] - prev_temp
        
        # Get temperature emoji and color
        temp_emoji = get_temp_emoji(record['temp'])
        weather_icon = get_weather_icon(record['description'])
        temp_color = get_temp_color(record['temp'])
        
        # Create styled card
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {temp_color}33 0%, {temp_color}11 100%);
                        border-radius: 15px; padding: 15px; border-left: 4px solid {temp_color};'>
                <h3 style='margin: 0; color: white;'>{weather_icon} {record['city']}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.metric(
                "Temperature", 
                f"{temp_emoji} {record['temp']:.1f}°C",
                delta=f"{temp_delta:+.1f}°C" if temp_delta is not None else None
            )
        
        with col2:
            st.metric(
                "Feels Like",
                f"{record['feels_like']:.1f}°C"
            )
        
        if show_metrics:
            col3, col4 = st.columns(2)
            with col3:
                st.markdown(f"**💧 Humidity**\\n{record['humidity']}%")
                st.markdown(f"**💨 Wind**\\n{record['wind']} m/s")
            with col4:
                st.markdown(f"**🔽 Pressure**\\n{record['pressure']} hPa")
                st.markdown(f"**{weather_icon} Weather**\\n{record['description']}")
        else:
            st.markdown(f"**{weather_icon}** {record['description']}")
        
        st.caption(f"🕒 Updated: {record['time']}")
        st.divider()


# Comparison table
if show_comparison and len(current_data) > 1:
    st.markdown("---")
    st.markdown("<h2 style='color: white;'>📊 City Comparison</h2>", unsafe_allow_html=True)
    
    comparison_df = pd.DataFrame(current_data)
    comparison_df = comparison_df[['city', 'temp', 'feels_like', 'humidity', 'wind', 'pressure', 'description']]
    comparison_df.columns = ['City', 'Temp (°C)', 'Feels Like (°C)', 'Humidity (%)', 'Wind (m/s)', 'Pressure (hPa)', 'Weather']
    
    # Style the dataframe
    st.dataframe(
        comparison_df.style.background_gradient(cmap='RdYlBu_r', subset=['Temp (°C)', 'Feels Like (°C)'])
                          .background_gradient(cmap='Blues', subset=['Humidity (%)'])
                          .format({'Temp (°C)': '{:.1f}', 'Feels Like (°C)': '{:.1f}', 'Wind (m/s)': '{:.1f}'}),
        use_container_width=True,
        hide_index=True
    )
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        hottest = comparison_df.loc[comparison_df['Temp (°C)'].idxmax()]
        st.metric("🔥 Hottest City", hottest['City'], f"{hottest['Temp (°C)']:.1f}°C")
    with col2:
        coldest = comparison_df.loc[comparison_df['Temp (°C)'].idxmin()]
        st.metric("🥶 Coldest City", coldest['City'], f"{coldest['Temp (°C)']:.1f}°C")
    with col3:
        most_humid = comparison_df.loc[comparison_df['Humidity (%)'].idxmax()]
        st.metric("💧 Most Humid", most_humid['City'], f"{most_humid['Humidity (%)']:.0f}%")
    with col4:
        windiest = comparison_df.loc[comparison_df['Wind (m/s)'].idxmax()]
        st.metric("💨 Windiest", windiest['City'], f"{windiest['Wind (m/s)']:.1f} m/s")


if show_charts and selected_cities:
    st.markdown("---")

    # Temperature chart over time
    st.markdown("<h2 style='color: white;'>📈 Historical Data Visualization</h2>", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns([3, 1], gap="large")
    
    with chart_col2:
        st.markdown("#### Chart Controls")
        city_for_chart = st.selectbox(
            "Select city",
            selected_cities,
            label_visibility="collapsed",
            key="city_selector"
        )
        metric_choice = st.radio(
            "Metric to display",
            ["🌡️ Temperature", "💧 Humidity", "🔽 Pressure"],
            horizontal=False,
            label_visibility="collapsed"
        )
        
        # Show current value
        current = next((d for d in current_data if d['city'] == city_for_chart), None)
        if current:
            metric_name = metric_choice.split()[1]
            if "Temperature" in metric_choice:
                st.info(f"**Current:** {current['temp']:.1f}°C")
            elif "Humidity" in metric_choice:
                st.info(f"**Current:** {current['humidity']}%")
            else:
                st.info(f"**Current:** {current['pressure']} hPa")
    
    with chart_col1:
        df_city = get_history_df(city_for_chart)
        if df_city.empty:
            st.info("📊 Not enough historical data yet. Data will appear after a few updates.")
        else:
            df_city = df_city.set_index("time")
            
            # Display selected metric
            if "Temperature" in metric_choice:
                st.line_chart(df_city["temp"], use_container_width=True, color="#e74c3c")
                if not df_city.empty:
                    st.caption(f"📊 Range: {df_city['temp'].min():.1f}°C - {df_city['temp'].max():.1f}°C | Average: {df_city['temp'].mean():.1f}°C | Data points: {len(df_city)}")
            elif "Humidity" in metric_choice:
                st.line_chart(df_city["humidity"], use_container_width=True, color="#3498db")
                if not df_city.empty:
                    st.caption(f"📊 Range: {df_city['humidity'].min():.0f}% - {df_city['humidity'].max():.0f}% | Average: {df_city['humidity'].mean():.0f}% | Data points: {len(df_city)}")
            else:  # Pressure
                st.line_chart(df_city["pressure"], use_container_width=True, color="#9b59b6")
                if not df_city.empty:
                    st.caption(f"📊 Range: {df_city['pressure'].min():.0f} - {df_city['pressure'].max():.0f} hPa | Average: {df_city['pressure'].mean():.0f} hPa | Data points: {len(df_city)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.7); padding: 20px;'>
        <p style='margin: 5px;'>⚡ Data provided by <a href='https://openweathermap.org/' style='color: #3498db;'>OpenWeather API</a></p>
        <p style='margin: 5px;'>🚀 Built with <a href='https://streamlit.io/' style='color: #3498db;'>Streamlit</a></p>
        <p style='margin: 5px; font-size: 0.9rem;'>Made with ❤️ for weather enthusiasts</p>
    </div>
""", unsafe_allow_html=True)

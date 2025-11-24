from typing import Dict, Optional
import requests
import streamlit as st
from datetime import datetime

# Application settings
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2

# Temperature thresholds
TEMP_COLD = 10
TEMP_COOL = 20
TEMP_WARM = 25
TEMP_HOT = 30

def validate_api_key(api_key: Optional[str]) -> bool:
    if not api_key:
        return False
    if len(api_key) < 10:
        return False
    return True

def get_temp_emoji(temp: float) -> str:
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
    if temp < TEMP_COLD:
        return "#3498db"
    elif temp < TEMP_COOL:
        return "#2ecc71"
    elif temp < TEMP_WARM:
        return "#f39c12"
    elif temp < TEMP_HOT:
        return "#e67e22"
    else:
        return "#e74c3c"


def fetch_weather(city: str, api_key: Optional[str], base_url: str) -> Optional[Dict]:
    if not validate_api_key(api_key):
        st.error("Missing or invalid API key.")
        return None

    params = {
        "q": city.strip(),
        "appid": api_key,
        "units": "metric",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(base_url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if "main" not in data or "weather" not in data:
                st.error(f"Invalid API response for {city}")
                return None

            main = data["main"]
            weather_desc = data["weather"][0]["description"].title()
            wind_speed = data.get("wind", {}).get("speed", 0)
            now = datetime.now()

            return {
                "city": city,
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "temp": main["temp"],
                "feels_like": main["feels_like"],
                "humidity": main["humidity"],
                "pressure": main["pressure"],
                "wind": wind_speed,
                "description": weather_desc,
            }
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                continue
            st.warning(f"Timeout fetching data for {city}.")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.error(f"❌ City '{city}' not found.")
            elif e.response.status_code == 401:
                st.error("❌ Invalid API key.")
            else:
                st.error(f"❌ HTTP error for {city}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Network error for {city}: {str(e)}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            st.error(f"Error parsing data for {city}: {str(e)}")
            return None
    
    return None

def init_session_state():
    if "prev_temps" not in st.session_state:
        st.session_state.prev_temps = {}

import streamlit as st
import pandas as pd
from utils import get_temp_emoji, get_weather_icon, get_temp_color
from config import CITIES_BY_REGION

def render_country_buttons():
    st.sidebar.markdown("#### 🌍 Quick Select by Country")
    
    regions = {
        "🌏 Asia & Middle East": ['🇻🇳', '🇯🇵', '🇰🇷', '🇨🇳', '🇹🇭', '🇸🇬', '🇲🇾', '🇮🇩', '🇵🇭', '🇮🇳', '🇦🇪', '🇸🇦', '🇹🇷', '🇮🇱'],
        "🌎 Americas": ['🇺🇸', '🇨🇦', '🇲🇽', '🇧🇷', '🇦🇷', '🇨🇱', '🇨🇴', '🇵🇪'],
        "🌍 Europe": ['🇬🇧', '🇫🇷', '🇩🇪', '🇮🇹', '🇪🇸', '🇳🇱', '🇧🇪', '🇨🇭', '🇦🇹', '🇵🇱', '🇨🇿', '🇭🇺', '🇷🇺', '🇺🇦', '🇸🇪', '🇳🇴', '🇩🇰', '🇫🇮', '🇮🇪', '🇵🇹', '🇬🇷'],
        "🌍 Africa": ['🇪🇬', '🇿🇦', '🇳🇬', '🇰🇪', '🇲🇦', '🇹🇳'],
        "🌏 Oceania": ['🇦🇺', '🇳🇿']
    }
    
    for region_name, flags in regions.items():
        with st.sidebar.expander(region_name, expanded=False):
            countries = [k for k in CITIES_BY_REGION.keys() if any(flag in k for flag in flags)]
            cols = st.columns(2)
            for i, country in enumerate(countries):
                with cols[i % 2]:
                    if st.button(country, key=f"btn_{country}", use_container_width=True):
                        st.session_state.selected_region = country
                        st.rerun()


def render_weather_card(record, show_metrics=True):    
    city = record['city']
    
    # Calculate temperature delta
    temp_delta = None
    if city in st.session_state.prev_temps:
        temp_delta = record['temp'] - st.session_state.prev_temps[city]
    st.session_state.prev_temps[city] = record['temp']
    
    # Get styling elements
    temp_emoji = get_temp_emoji(record['temp'])
    weather_icon = get_weather_icon(record['description'])
    temp_color = get_temp_color(record['temp'])
    
    # Card header
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {temp_color}40 0%, {temp_color}15 100%);
                    border-radius: 20px; padding: 20px; border-left: 4px solid {temp_color};
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    animation: fadeInUp 0.6s ease-out;'>
            <h3 style='margin: 0; color: white; font-weight: 600; 
                       letter-spacing: -0.02em; font-size: 1.5rem;'>
                {weather_icon} {city}
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Temperature metrics
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(
            "Temperature",
            f"{temp_emoji} {record['temp']:.1f}°C",
            delta=f"{temp_delta:+.1f}°C" if temp_delta is not None else None
        )
    with col2:
        st.metric("Feels Like", f"{record['feels_like']:.1f}°C")
    
    # Additional metrics
    if show_metrics:
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"**💧 Humidity**  \n{record['humidity']}%")
            st.markdown(f"**💨 Wind**  \n{record['wind']} m/s")
        with col4:
            st.markdown(f"**🔽 Pressure**  \n{record['pressure']} hPa")
            st.markdown(f"**{weather_icon} Weather**  \n{record['description']}")
    else:
        st.markdown(f"**{weather_icon}** {record['description']}")
    
    st.caption(f"📅 {record['date']} | 🕒 {record['time']}")
    st.divider()


def render_comparison_table(current_data):    
    st.markdown("""
        <div style='margin: 3rem 0 1rem 0;'>
            <div style='height: 1px; background: linear-gradient(90deg, 
                transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);'></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='color: white; font-weight: 600; letter-spacing: -0.02em;'>📊 City Comparison</h2>", 
                unsafe_allow_html=True)
    
    comparison_df = pd.DataFrame(current_data)
    comparison_df = comparison_df[['city', 'temp', 'feels_like', 'humidity', 'wind', 'pressure', 'description']]
    comparison_df.columns = ['City', 'Temp (°C)', 'Feels Like (°C)', 'Humidity (%)', 'Wind (m/s)', 'Pressure (hPa)', 'Weather']
    
    st.dataframe(
        comparison_df.style.format({
            'Temp (°C)': '{:.1f}',
            'Feels Like (°C)': '{:.1f}',
            'Wind (m/s)': '{:.1f}',
            'Humidity (%)': '{:.0f}',
            'Pressure (hPa)': '{:.0f}'
        }).background_gradient(cmap='RdYlBu_r', subset=['Temp (°C)', 'Feels Like (°C)'])
          .background_gradient(cmap='Blues', subset=['Humidity (%)']),
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


def render_header():
    st.markdown("""
        <div style='text-align: center; animation: fadeInUp 0.5s ease-out;'>
            <h1 style='font-size: 4rem; margin-bottom: 0; font-weight: 700; 
                       background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.8) 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       background-clip: text; letter-spacing: -0.04em;'>
                🌤️ Weather Dashboard
            </h1>
            <p style='color: rgba(255,255,255,0.85); font-size: 1.3rem; margin-top: 10px;
                      font-weight: 400; letter-spacing: -0.02em;'>
                Real-time weather data with beautiful animations
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
        <div style='margin-top: 4rem;'>
            <div style='height: 1px; background: linear-gradient(90deg, 
                transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);'></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; color: rgba(255,255,255,0.7); padding: 40px 20px;
                    animation: fadeInUp 1s ease-out;'>
            <p style='margin: 8px; font-size: 0.95rem; font-weight: 400; letter-spacing: -0.01em;'>
                ⚡ Data provided by <a href='https://openweathermap.org/' 
                   style='color: rgba(255,255,255,0.9); text-decoration: none; 
                          border-bottom: 1px solid rgba(255,255,255,0.3);
                          transition: all 0.3s ease;'
                   onmouseover='this.style.borderBottom="1px solid rgba(255,255,255,0.8)"'
                   onmouseout='this.style.borderBottom="1px solid rgba(255,255,255,0.3)"'>
                   OpenWeather API
                </a>
            </p>
            <p style='margin: 8px; font-size: 0.95rem; font-weight: 400; letter-spacing: -0.01em;'>
                🚀 Built with <a href='https://streamlit.io/' 
                   style='color: rgba(255,255,255,0.9); text-decoration: none;
                          border-bottom: 1px solid rgba(255,255,255,0.3);
                          transition: all 0.3s ease;'
                   onmouseover='this.style.borderBottom="1px solid rgba(255,255,255,0.8)"'
                   onmouseout='this.style.borderBottom="1px solid rgba(255,255,255,0.3)"'>
                   Streamlit
                </a>
            </p>
            <p style='margin: 16px 0 0 0; font-size: 0.85rem; opacity: 0.6; 
                      font-weight: 300; letter-spacing: 0.02em;'>
                Designed with ❤️ for weather enthusiasts
            </p>
        </div>
    """, unsafe_allow_html=True)

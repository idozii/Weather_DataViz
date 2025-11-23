# Weather Realtime Dashboard 🌤️

A beautiful, real-time weather dashboard built with Streamlit that displays current weather conditions and historical data for multiple cities.

## Link

[text](https://weathertracking-idozii.streamlit.app/)

## Features

- 🌍 **Multi-city monitoring** - Track weather for multiple cities simultaneously
- 🔄 **Auto-refresh** - Updates every 60 seconds automatically
- 📊 **Historical charts** - View temperature, humidity, and pressure trends
- 📱 **Responsive design** - Works on desktop and mobile
- 🎨 **Modern UI** - Clean interface with emojis and intuitive controls

## Prerequisites

- Python 3.8 or higher
- OpenWeather API key (free tier available)

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your OpenWeather API key:**
   - Visit [OpenWeather](https://openweathermap.org/)
   - Sign up for a free account
   - Go to "My API keys" section
   - Copy your API key

4. **Create a `.env` file** in the project root:
   ```bash
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the application:
```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## Configuration

You can customize the following in `app.py`:

- `DEFAULT_CITIES` - List of default cities to monitor
- `REFRESH_INTERVAL_MS` - Auto-refresh interval (default: 60 seconds)
- `MAX_HISTORY_RECORDS` - Maximum historical data points per city (default: 200)

## Deployment

### Streamlit Cloud (Recommended)

1. Push your code to GitHub (without the `.env` file)
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Deploy your app
4. Add your API key in Streamlit Cloud secrets:
   ```toml
   OPENWEATHER_API_KEY = "your_actual_api_key_here"
   ```

### Other Platforms

The app can be deployed on:
- Heroku
- Railway
- Render
- Any platform supporting Python web apps

## Troubleshooting

### "Invalid API key" error
- Wait 10-120 minutes after creating your API key for it to activate
- Check that your API key is correctly copied in the `.env` file
- Verify your key status at [OpenWeather API keys](https://home.openweathermap.org/api_keys)

### "City not found" error
- Ensure city names are in English
- Check spelling carefully
- Try using the exact name from OpenWeather's city list

## License

MIT License - feel free to use and modify for your projects!

## Credits

- Weather data provided by [OpenWeather API](https://openweathermap.org/)
- Built with [Streamlit](https://streamlit.io/)

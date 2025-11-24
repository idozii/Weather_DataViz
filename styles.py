def get_custom_css():
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; } }
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; -webkit-font-smoothing: antialiased; }
.main { background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); background-size: 200% 200%; animation: gradient 15s ease infinite; }
.stMetric { background: rgba(255, 255, 255, 0.08); padding: 20px; border-radius: 16px; backdrop-filter: blur(20px) saturate(180%); border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); animation: fadeInUp 0.6s ease-out; }
.stMetric:hover { transform: translateY(-5px) scale(1.02); background: rgba(255, 255, 255, 0.12); box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15); }
div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 600; letter-spacing: -0.02em; background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.9) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
h1, h2, h3, h4, h5, h6 { color: white; font-weight: 600; letter-spacing: -0.03em; text-shadow: 0 2px 12px rgba(0,0,0,0.15); animation: fadeInUp 0.7s ease-out; }
.stSelectbox label, .stMultiSelect label, .stCheckbox label { color: white !important; font-weight: 500; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background: rgba(255, 255, 255, 0.1) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 12px !important; transition: all 0.3s ease !important; }
div[data-baseweb="select"] > div:hover, div[data-baseweb="input"] > div:hover { background: rgba(255, 255, 255, 0.15) !important; transform: translateY(-2px); }
.stCheckbox:hover { transform: translateX(4px); }
div[data-testid="stMarkdownContainer"] { animation: fadeInUp 0.7s ease-out; }
[data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255, 255, 255, 0.1); }
html { scroll-behavior: smooth; }
.dataframe { animation: fadeInUp 0.8s ease-out; }
table { border-radius: 12px !important; overflow: hidden; }
.stCaption { color: rgba(255, 255, 255, 0.7) !important; }
</style>"""

def hide_streamlit_elements():
    return """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>"""

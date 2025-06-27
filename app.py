import streamlit as st
import requests
import joblib
from streamlit_geolocation import streamlit_geolocation

# Page settings
st.set_page_config(page_title="Crop Recommender", page_icon="🌾", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: black;
    }
    h1, h2, h3, h4, p, label, div, span, input {
        color: white !important;
    }
    .stButton>button {
        background-color: red;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: darkred;
        color: white;
    }
    .stNumberInput>div>div>input {
        background-color: #222 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# API Key
api_key = "d56fb2ef217db80dee4a005b2c8e25e4"

# Weather functions
def get_weather(lat, lon):
    res = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    ).json()
    if "main" not in res:
        raise ValueError("Weather data not available.")
    return round(res['main']['temp'],2), round(res['main']['humidity'],2), round(res.get('rain', {}).get('1h',0.0),2)

def get_location_name(lat, lon):
    try:
        headers = {"User-Agent": "crop-recommender/1.0"}
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        res = requests.get(url, headers=headers).json()
        return res.get("display_name", "Unknown Location")
    except:
        return "Unknown Location"

# Fertilizer data
fertilizer_data = {
    "rice": "Urea: 50kg/ha, DAP: 25kg/ha",
    "wheat": "Urea: 40kg/ha, DAP: 20kg/ha",
    "maize": "Urea: 55kg/ha, MOP: 20kg/ha",
    "cotton": "Urea: 60kg/ha, SSP: 30kg/ha",
    "sugarcane": "Urea: 80kg/ha, DAP: 40kg/ha, MOP: 30kg/ha",
}
def get_fertilizer_recommendation(crop):
    return fertilizer_data.get(crop.lower(), "Generic: Urea 45kg/ha, DAP 20kg/ha")

# Session State defaults
if "weather_data" not in st.session_state:
    st.session_state.weather_data = {"temp": 0.0, "humidity": 0.0, "rainfall": 0.0}
if "location_clicked" not in st.session_state:
    st.session_state.location_clicked = False
if "location_name" not in st.session_state:
    st.session_state.location_name = None
if "weather_error" not in st.session_state:
    st.session_state.weather_error = None

# Layout
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.title("🌾 Crop Recommendation System")

    # Location Auto-fill Section
    st.subheader("📍 Optional Weather Auto-fill")
    st.caption("Click to use your location for autofill:")

    location = streamlit_geolocation()
    if location:
        st.session_state.location_clicked = True
        lat, lon = location['latitude'], location['longitude']
        st.session_state.location_name = get_location_name(lat, lon)
        try:
            temp, humidity, rainfall = get_weather(lat, lon)
            st.session_state.weather_data = {
                "temp": temp,
                "humidity": humidity,
                "rainfall": rainfall
            }
            st.session_state.weather_error = None
        except Exception as e:
            st.session_state.weather_error = f"⚠️ Could not fetch weather data: {e}"

    # Show location and weather only if clicked
    if st.session_state.location_clicked:
        if st.session_state.location_name:
            st.success(f"📍 You are in: **{st.session_state.location_name}**")
        if st.session_state.weather_error:
            st.error(st.session_state.weather_error)
        else:
            wd = st.session_state.weather_data
            st.info(f"✅ Auto-filled Weather: 🌡️ {wd['temp']}°C | 💧 {wd['humidity']}% | 🌧️ {wd['rainfall']} mm")

    st.subheader("🧪 Enter Soil and Weather Data")
    N = st.number_input("Nitrogen", min_value=0)
    P = st.number_input("Phosphorus", min_value=0)
    K = st.number_input("Potassium", min_value=0)
    temperature = st.number_input("Temperature (°C)", value=st.session_state.weather_data["temp"])
    humidity = st.number_input("Humidity (%)", value=st.session_state.weather_data["humidity"])
    ph = st.number_input("pH", min_value=0.0, max_value=14.0)
    rainfall = st.number_input("Rainfall (mm)", value=st.session_state.weather_data["rainfall"])

    if st.button("Predict Crop"):
        try:
            model = joblib.load("crop_recommendation_model.pkl")
            pred = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])[0]
            st.success(f"🌱 Recommended Crop: **{pred.upper()}**")
            recommendation = get_fertilizer_recommendation(pred)
            st.info(f"🧪 Fertilizer Recommendation:\n{recommendation}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

with col2:
    st.image(
        "https://images.app.goo.gl/jBgN5t1YUcQEivwL8"
        use_column_width=True
    )

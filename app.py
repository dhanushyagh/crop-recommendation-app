from streamlit_geolocation import streamlit_geolocation
import streamlit as st
import requests
import joblib

st.set_page_config(page_title="Crop Recommender", page_icon="🌾")
st.title("🌾 Crop Recommendation System")

api_key = "d56fb2ef217db80dee4a005b2c8e25e4"

#  Weather fetch helpers

def get_weather(lat, lon):
    res = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    ).json()
    if "main" not in res:
        raise ValueError("Weather data not available for this location.")
    return (
        round(res['main']['temp'], 2),
        round(res['main']['humidity'], 2),
        round(res.get('rain', {}).get('1h', 0.0), 2)
    )

def get_location_name(lat, lon):
    try:
        headers = {
            "User-Agent": "crop-recommender/1.0 (your_email@example.com)"
        }
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        res = requests.get(url, headers=headers).json()
        return res.get("display_name", "Unknown Location")
    except:
        return "Unknown Location"

# Session state for autofill 

if "weather_data" not in st.session_state:
    st.session_state.weather_data = {
        "temp": 0.0,
        "humidity": 0.0,
        "rainfall": 0.0
    }

# Optional Location Autofill 

st.subheader("📍 Optional: Auto-fill Weather Data from My Location")
st.caption("If you want, click the button below to use your device location and fetch local weather automatically.")

if "show_location_result" not in st.session_state:
    st.session_state.show_location_result = False

if st.button("Auto-fill Weather from My Location"):
    loc = streamlit_geolocation()
    if loc:
        lat, lon = loc['latitude'], loc['longitude']
        location_name = get_location_name(lat, lon)
        st.session_state.location_name = location_name
        st.session_state.show_location_result = True
        
        try:
            temp, humidity, rainfall = get_weather(lat, lon)
            st.session_state.weather_data = {
                "temp": temp,
                "humidity": humidity,
                "rainfall": rainfall
            }
            st.session_state.weather_message = f"✅ Weather auto-filled: 🌡️ {temp}°C | 💧 {humidity}% | 🌧️ {rainfall} mm"
            st.session_state.weather_error = None
        except Exception as e:
            st.session_state.weather_message = None
            st.session_state.weather_error = f"⚠️ Could not fetch weather data: {e}"
    else:
        st.session_state.location_name = "Unknown Location"
        st.session_state.show_location_result = True
        st.session_state.weather_message = None
        st.session_state.weather_error = "⚠️ Could not get location from device."

# Show results *only* if user pressed the button
if st.session_state.show_location_result:
    if "location_name" in st.session_state:
        st.success(f"📍 You are in: **{st.session_state.location_name}**")
    if st.session_state.weather_message:
        st.success(st.session_state.weather_message)
    if st.session_state.weather_error:
        st.error(st.session_state.weather_error)
# Inputs Section (always visible) 

st.subheader("🧪 Enter Soil and Weather Data")

N = st.number_input("Nitrogen", min_value=0)
P = st.number_input("Phosphorus", min_value=0)
K = st.number_input("Potassium", min_value=0)

temperature = st.number_input(
    "Temperature (°C)",
    value=st.session_state.weather_data["temp"]
)
humidity = st.number_input(
    "Humidity (%)",
    value=st.session_state.weather_data["humidity"]
)
ph = st.number_input(
    "pH",
    min_value=0.0, max_value=14.0
)
rainfall = st.number_input(
    "Rainfall (mm)",
    value=st.session_state.weather_data["rainfall"]
)

# Prediction Button 

if st.button("Predict Crop"):
    try:
        model = joblib.load("crop_recommendation_model.pkl")
        pred = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])[0]
        st.success(f"🌱 Recommended Crop: **{pred.upper()}**")
    except Exception as e:
        st.error(f"⚠️ Something went wrong with prediction: {e}")

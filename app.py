from streamlit_geolocation import streamlit_geolocation
import streamlit as st
import requests
import joblib

st.set_page_config(page_title="Crop Recommender", page_icon="🌾")
st.title("🌾 Crop Recommendation System")

api_key = "d56fb2ef217db80dee4a005b2c8e25e4"

# Weather fetch helpers 

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

#  UI 

st.subheader("📍 Choose how to enter weather data")

# Option for user to choose
mode = st.radio(
    "How do you want to provide weather data?",
    ["Use my location", "Enter manually"]
)

# Default values
temp_default = 0.0
humidity_default = 0.0
rainfall_default = 0.0

if mode == "Use my location":
    st.info("Click the button below to get your current location.")
    loc = streamlit_geolocation()
    
    if loc:
        lat, lon = loc['latitude'], loc['longitude']
        location_name = get_location_name(lat, lon)
        st.success(f"📍 You are in: **{location_name}**")
        
        try:
            temp, humidity, rainfall = get_weather(lat, lon)
            st.success(f"🌡️ {temp}°C | 💧 {humidity}% | 🌧️ {rainfall} mm")
            temp_default = temp
            humidity_default = humidity
            rainfall_default = rainfall
        except Exception as e:
            st.error(f"⚠️ Could not fetch weather data: {e}")
    else:
        st.warning("👉 Allow location access or enter details manually below.")

else:
    st.info("You chose to enter weather data manually.")

#Inputs Section 

st.subheader("🧪 Enter Soil and Weather Data")

N = st.number_input("Nitrogen", min_value=0)
P = st.number_input("Phosphorus", min_value=0)
K = st.number_input("Potassium", min_value=0)
temperature = st.number_input("Temperature (°C)", value=temp_default)
humidity = st.number_input("Humidity (%)", value=humidity_default)
ph = st.number_input("pH", min_value=0.0, max_value=14.0)
rainfall = st.number_input("Rainfall (mm)", value=rainfall_default)

# Prediction Button 

if st.button("Predict Crop"):
    try:
        model = joblib.load("crop_recommendation_model.pkl")
        pred = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])[0]
        st.success(f"🌱 Recommended Crop: **{pred.upper()}**")
    except Exception as e:
        st.error(f"⚠️ Something went wrong with prediction: {e}")

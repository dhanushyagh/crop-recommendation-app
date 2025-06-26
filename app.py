from streamlit_geolocation import streamlit_geolocation
import streamlit as st
import requests
import joblib

st.set_page_config(page_title="Crop Recommender", page_icon="🌾")
st.title("🌾 Crop Recommendation System")

api_key = "d56fb2ef217db80dee4a005b2c8e25e4"

def get_weather(lat, lon):
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}").json()
    return round(res['main']['temp'],2), round(res['main']['humidity'],2), round(res.get('rain', {}).get('1h',0.0),2)

def get_location_name(lat, lon):
    res = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json").json()
    return res.get("display_name", "Unknown Location")

# Use the component
loc = streamlit_geolocation()
if loc:
    lat, lon = loc['latitude'], loc['longitude']
    st.success(f"📍 You are in: **{get_location_name(lat, lon)}**")
    temp, humidity, rainfall = get_weather(lat, lon)
    st.info(f"🌡️ {temp}°C | 💧 {humidity}% | 🌧️ {rainfall} mm")
else:
    temp = humidity = rainfall = 0.0

# Soil/weather inputs
st.subheader("🧪 Enter Soil and Weather Data")
N = st.number_input("Nitrogen", min_value=0)
P = st.number_input("Phosphorus", min_value=0)
K = st.number_input("Potassium", min_value=0)
temperature = st.number_input("Temperature (°C)", value=temp)
humidity = st.number_input("Humidity (%)", value=humidity)
ph = st.number_input("pH", min_value=0.0, max_value=14.0)
rainfall = st.number_input("Rainfall (mm)", value=rainfall)

# Predict
if st.button("Predict Crop"):
    try:
        model = joblib.load("crop_recommendation_model.pkl")
        pred = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])[0]
        st.success(f"🌱 Recommended Crop: **{pred.upper()}**")
    except:
        st.error("⚠️ Something went wrong with prediction.")

import streamlit as st
import requests
import joblib
from streamlit_javascript import st_javascript

st.set_page_config(page_title="Crop Recommendation", page_icon="🌾")
st.title("🌾 Crop Recommendation System")

api_key = "d56fb2ef217db80dee4a005b2c8e25e4" 

def get_weather(lat, lon, api_key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
        res = requests.get(url).json()
        temp = res['main']['temp']
        humidity = res['main']['humidity']
        rainfall = res.get('rain', {}).get('1h', 0.0)
        return round(temp, 2), round(humidity, 2), round(rainfall, 2)
    except:
        return 0.0, 0.0, 0.0

def get_location_name(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        res = requests.get(url).json()
        return res.get("display_name", "Unknown Location")
    except:
        return "Unknown Location"

# Step 1: Init session variables
if 'coords' not in st.session_state:
    st.session_state.coords = None

# Step 2: Button to get location
if st.button("📍 Get My Location"):
    coords = st_javascript("""await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                });
            },
            (err) => {
                reject(err.message);
            }
        );
    });""")
    st.session_state.coords = coords

# Step 3: If coords are stored in session, use them
if st.session_state.coords:
    lat = st.session_state.coords.get("latitude")
    lon = st.session_state.coords.get("longitude")

    location_name = get_location_name(lat, lon)
    temp, humidity, rainfall = get_weather(lat, lon, api_key)

    st.success(f"📍 You are in: {location_name}")
    st.info(f"🌡️ Temp: {temp}°C | 💧 Humidity: {humidity}% | 🌧️ Rainfall: {rainfall} mm")
else:
    temp, humidity, rainfall = 0.0, 0.0, 0.0

# Step 4: Input form
st.subheader("🧪 Enter Soil and Weather Data")
N = st.number_input("Nitrogen", min_value=0)
P = st.number_input("Phosphorus", min_value=0)
K = st.number_input("Potassium", min_value=0)
temperature = st.number_input("Temperature (°C)", value=temp)
humidity = st.number_input("Humidity (%)", value=humidity)
ph = st.number_input("pH", min_value=0.0, max_value=14.0)
rainfall = st.number_input("Rainfall (mm)", value=rainfall)

# Step 5: Prediction
if st.button("Predict Crop"):
    try:
        model = joblib.load("crop_recommendation_model.pkl")
        data = [[N, P, K, temperature, humidity, ph, rainfall]]
        prediction = model.predict(data)[0]
        st.success(f"🌱 Recommended Crop: **{prediction.upper()}**")
    except Exception as e:
        st.error("❌ Prediction failed. Check model or input.")

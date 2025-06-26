import streamlit as st
import requests
from streamlit_javascript import st_javascript
import joblib

st.set_page_config(page_title="Crop Recommender", page_icon="🌾")

st.title("🌾 Crop Recommendation System")

# Step 1: Get user location
if st.button("📍 Get my location"):
coords = st_javascript("""await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            resolve({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            });
        },
        (error) => {
            reject(error.message);
        }
    );
});""")

# Step 2: Use weather API
api_key = "d56fb2ef217db80dee4a005b2c8e25e4" 

def get_weather(lat, lon, api_key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        rainfall = data.get('rain' ,{}.get('1h',0.0)
        return round(temp, 2), round(humidity, 2) ,round(rainfall,2)
    except:
        return None, None, None
# Get temperature and humidity
if coords:
    lat = coords.get("latitude")
    lon = coords.get("longitude")
    st.success(f"📍 Location detected: ({lat:.2f}, {lon:.2f})")
     temp, humidity ,rainfall= get_weather(lat, lon, api_key)
else:
    temp, humidity, rainfall= "", "",""
    st.warning("📍 Please allow location access above to auto-fill weather data.")

# Step 3: Input Fields
st.subheader("🧪 Enter Soil and Weather Data")

N = st.number_input("Nitrogen", min_value=0)
P = st.number_input("Phosphorus", min_value=0)
K = st.number_input("Potassium", min_value=0)
temperature = st.number_input("Temperature (°C)", value=temp if temp else 0.0)
humidity = st.number_input("Humidity (%)", value=humidity if humidity else 0.0)
ph = st.number_input("pH", min_value=0.0, max_value=14.0)
rainfall = st.number_input("Rainfall (mm)", min_value=0.0)

# Step 4: Load Model and Predict
if st.button("Predict Crop"):
    model = joblib.load("crop_recommendation_model.pkl")
    input_data = [[N, P, K, temperature, humidity, ph, rainfall]]
    prediction = model.predict(input_data)[0]
    st.success(f"🌱 Recommended Crop: **{prediction.upper()}**")

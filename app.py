from streamlit_geolocation import streamlit_geolocation
import streamlit as st
import requests
import joblib

# ---------- Custom Page Setup ----------
st.set_page_config(page_title="Crop Recommender", page_icon="🌾")

# ---------- Custom Styling ----------
st.markdown("""
    <style>
    body {
        background-color: #f8f4e3;
    }
    .stButton > button {
        background-color: #e63946;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
    }
    .stButton > button:hover {
        background-color: #d62828;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- App Title ----------
st.title("🌾 Crop Recommendation System")

api_key = "d56fb2ef217db80dee4a005b2c8e25e4"

# ---------- Weather fetch helpers ----------

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

# ---------- Fertilizer recommendation dictionary ----------

fertilizer_data = {
    "rice": "Nitrogen: 100 kg/ha, Phosphorus: 50 kg/ha, Potassium: 50 kg/ha",
    "maize": "Nitrogen: 150 kg/ha, Phosphorus: 60 kg/ha, Potassium: 50 kg/ha",
    "chickpea": "Nitrogen: 20 kg/ha, Phosphorus: 40 kg/ha, Potassium: 20 kg/ha",
    "kidneybeans": "Nitrogen: 25 kg/ha, Phosphorus: 50 kg/ha, Potassium: 25 kg/ha",
    "pegionbeans": "Nitrogen: 20 kg/ha, Phosphorus: 50 kg/ha, Potassium: 20 kg/ha",
    "mothbeans": "Nitrogen: 20 kg/ha, Phosphorus: 30 kg/ha, Potassium: 20 kg/ha",
    "mungbeans": "Nitrogen: 20 kg/ha, Phosphorus: 40 kg/ha, Potassium: 20 kg/ha",
    "blackgram": "Nitrogen: 20 kg/ha, Phosphorus: 40 kg/ha, Potassium: 20 kg/ha",
    "lentil": "Nitrogen: 20 kg/ha, Phosphorus: 40 kg/ha, Potassium: 20 kg/ha",
    "pomegranate": "Nitrogen: 250 g/tree/year, Phosphorus: 125 g/tree/year, Potassium: 125 g/tree/year",
    "banana": "Nitrogen: 200 g/plant/year, Phosphorus: 100 g/plant/year, Potassium: 300 g/plant/year",
    "mango": "Nitrogen: 750 g/tree/year, Phosphorus: 500 g/tree/year, Potassium: 750 g/tree/year",
    "grapes": "Nitrogen: 150 kg/ha, Phosphorus: 120 kg/ha, Potassium: 300 kg/ha",
    "watermelon": "Nitrogen: 100 kg/ha, Phosphorus: 50 kg/ha, Potassium: 80 kg/ha",
    "muskmelon": "Nitrogen: 80 kg/ha, Phosphorus: 40 kg/ha, Potassium: 60 kg/ha",
    "apple": "Nitrogen: 500 g/tree/year, Phosphorus: 250 g/tree/year, Potassium: 300 g/tree/year",
    "orange": "Nitrogen: 400 g/tree/year, Phosphorus: 200 g/tree/year, Potassium: 300 g/tree/year",
    "papaya": "Nitrogen: 200 g/plant/year, Phosphorus: 150 g/plant/year, Potassium: 200 g/plant/year",
    "coconut": "Nitrogen: 500 g/palm/year, Phosphorus: 320 g/palm/year, Potassium: 1200 g/palm/year",
    "cotton": "Nitrogen: 100 kg/ha, Phosphorus: 50 kg/ha, Potassium: 50 kg/ha",
    "jute": "Nitrogen: 60 kg/ha, Phosphorus: 30 kg/ha, Potassium: 30 kg/ha",
    "coffee": "Nitrogen: 120 kg/ha, Phosphorus: 90 kg/ha, Potassium: 120 kg/ha",
}

def get_fertilizer_recommendation(crop):
    return fertilizer_data.get(crop.lower(), "Generic recommendation: Nitrogen: 45 kg/ha, Phosphorus: 20 kg/ha")

# ---------- Session State Setup ----------

if "weather_data" not in st.session_state:
    st.session_state.weather_data = {
        "temp": 0.0,
        "humidity": 0.0,
        "rainfall": 0.0
    }

if "show_location_result" not in st.session_state:
    st.session_state.show_location_result = False

if "location_name" not in st.session_state:
    st.session_state.location_name = None

if "weather_message" not in st.session_state:
    st.session_state.weather_message = None

if "weather_error" not in st.session_state:
    st.session_state.weather_error = None

# ---------- Optional Location Autofill ----------

st.subheader("📍 Optional Weather Auto-fill")

cols = st.columns([8, 1])
with cols[0]:
    st.caption("Click to use your location for autofill:")
with cols[1]:
    clicked = streamlit_geolocation()

if clicked:
    lat, lon = clicked['latitude'], clicked['longitude']
    st.session_state.show_location_result = True
    st.session_state.location_name = get_location_name(lat, lon)

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

# ---------- Show Results ONLY if Clicked ----------

if st.session_state.show_location_result:
    if st.session_state.location_name:
        st.success(f"📍 You are in: **{st.session_state.location_name}**")
    if st.session_state.weather_message:
        st.info(st.session_state.weather_message)
    if st.session_state.weather_error:
        st.error(st.session_state.weather_error)

# ---------- Inputs Section with Farmer Photos on Both Sides, Vertically Centered ----------

st.subheader("🧪 Enter Soil and Weather Data")

left_col, center_col, right_col = st.columns([1, 5, 1])

with left_col:
    st.markdown(
        """
        <div style='display:flex; justify-content:center; align-items:center; height:80vh;'>
            <img src='malefarmer.jpeg' style='height:60vh; object-fit:contain;' alt='Male Farmer'>
        </div>
        """,
        unsafe_allow_html=True
    )

with center_col:
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
        min_value=5.0, max_value=14.0
    )
    rainfall = st.number_input(
        "Rainfall (mm)",
        value=st.session_state.weather_data["rainfall"]
    )

with right_col:
    st.markdown(
        """
        <div style='display:flex; justify-content:center; align-items:center; height:80vh;'>
            <img src='femalefarmer.jpeg' style='height:60vh; object-fit:contain;' alt='Female Farmer'>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Prediction Button ----------

if st.button("Predict Crop"):
    try:
        model = joblib.load("crop_recommendation_model.pkl")
        pred = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])[0]
        
        st.success(f"🌱 Recommended Crop: **{pred.upper()}**")

        recommendation = get_fertilizer_recommendation(pred)
        st.info(f"🧪 Fertilizer Recommendation:\n{recommendation}")

    except Exception as e:
        st.error(f"⚠️ Something went wrong with prediction: {e}")

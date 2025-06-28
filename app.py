from streamlit_geolocation import streamlit_geolocation
import streamlit as st
import requests
import joblib

#  Custom Page Setup 
st.set_page_config(page_title="Crop Recommender", page_icon="🌾")

# Custom Styling 
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

#  App Title 
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

# Fertilizer recommendation dictionary 

fertilizer_data = {
    "rice": (
        "Nitrogen: 100 kg/ha (e.g., Urea)\n"
        "Phosphorus: 50 kg/ha (e.g., DAP)\n"
        "Potassium: 50 kg/ha (e.g., MOP)\n"
        "Split application recommended at transplanting and tillering."
    ),
    "maize": (
        "Nitrogen: 150 kg/ha (e.g., Urea)\n"
        "Phosphorus: 60 kg/ha (e.g., DAP)\n"
        "Potassium: 50 kg/ha (e.g., MOP)\n"
        "Apply in 2 splits: sowing and knee-high stage."
    ),
    "chickpea": (
        "Nitrogen: 20 kg/ha (e.g., Urea)\n"
        "Phosphorus: 40 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 20 kg/ha (e.g., MOP)\n"
        "Basal application recommended before sowing."
    ),
    "kidneybeans": (
        "Nitrogen: 25 kg/ha (e.g., Urea)\n"
        "Phosphorus: 50 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 25 kg/ha (e.g., MOP)\n"
        "Apply as basal before sowing."
    ),
    "pegionbeans": (
        "Nitrogen: 20 kg/ha (e.g., Urea)\n"
        "Phosphorus: 50 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 20 kg/ha (e.g., MOP)\n"
        "Apply as basal dose at sowing."
    ),
    "mothbeans": (
        "Nitrogen: 20 kg/ha (e.g., Urea)\n"
        "Phosphorus: 30 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 20 kg/ha (e.g., MOP)\n"
        "Basal application recommended."
    ),
    "mungbeans": (
        "Nitrogen: 20 kg/ha (e.g., Urea)\n"
        "Phosphorus: 40 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 20 kg/ha (e.g., MOP)\n"
        "Apply before sowing."
    ),
    "blackgram": (
        "Nitrogen: 20 kg/ha (e.g., Urea)\n"
        "Phosphorus: 40 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 20 kg/ha (e.g., MOP)\n"
        "Basal application at sowing."
    ),
    "lentil": (
        "Nitrogen: 20 kg/ha (e.g., Urea)\n"
        "Phosphorus: 40 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 20 kg/ha (e.g., MOP)\n"
        "Apply as basal dose."
    ),
    "pomegranate": (
        "Nitrogen: 250 g/tree/year (e.g., Urea)\n"
        "Phosphorus: 125 g/tree/year (e.g., DAP)\n"
        "Potassium: 125 g/tree/year (e.g., MOP)\n"
        "Apply in two splits annually."
    ),
    "banana": (
        "Nitrogen: 200 g/plant/year (e.g., Urea)\n"
        "Phosphorus: 100 g/plant/year (e.g., DAP)\n"
        "Potassium: 300 g/plant/year (e.g., MOP)\n"
        "Split into 3-4 doses during growth."
    ),
    "mango": (
        "Nitrogen: 750 g/tree/year (e.g., Urea)\n"
        "Phosphorus: 500 g/tree/year (e.g., SSP/DAP)\n"
        "Potassium: 750 g/tree/year (e.g., MOP)\n"
        "Apply in two splits before monsoon and post-harvest."
    ),
    "grapes": (
        "Nitrogen: 150 kg/ha (e.g., Urea)\n"
        "Phosphorus: 120 kg/ha (e.g., DAP)\n"
        "Potassium: 300 kg/ha (e.g., MOP)\n"
        "Split application recommended at pruning and fruiting."
    ),
    "watermelon": (
        "Nitrogen: 100 kg/ha (e.g., Urea)\n"
        "Phosphorus: 50 kg/ha (e.g., DAP)\n"
        "Potassium: 80 kg/ha (e.g., MOP)\n"
        "Basal plus top dressing at vining."
    ),
    "muskmelon": (
        "Nitrogen: 80 kg/ha (e.g., Urea)\n"
        "Phosphorus: 40 kg/ha (e.g., DAP)\n"
        "Potassium: 60 kg/ha (e.g., MOP)\n"
        "Apply in 2 splits."
    ),
    "apple": (
        "Nitrogen: 500 g/tree/year (e.g., Urea)\n"
        "Phosphorus: 250 g/tree/year (e.g., SSP/DAP)\n"
        "Potassium: 300 g/tree/year (e.g., MOP)\n"
        "Apply in spring before flowering."
    ),
    "orange": (
        "Nitrogen: 400 g/tree/year (e.g., Urea)\n"
        "Phosphorus: 200 g/tree/year (e.g., SSP/DAP)\n"
        "Potassium: 300 g/tree/year (e.g., MOP)\n"
        "Split between pre-monsoon and post-monsoon."
    ),
    "papaya": (
        "Nitrogen: 200 g/plant/year (e.g., Urea)\n"
        "Phosphorus: 150 g/plant/year (e.g., DAP)\n"
        "Potassium: 200 g/plant/year (e.g., MOP)\n"
        "Apply monthly in small doses."
    ),
    "coconut": (
        "Nitrogen: 500 g/palm/year (e.g., Urea)\n"
        "Phosphorus: 320 g/palm/year (e.g., SSP/DAP)\n"
        "Potassium: 1200 g/palm/year (e.g., MOP)\n"
        "Apply in two splits annually."
    ),
    "cotton": (
        "Nitrogen: 100 kg/ha (e.g., Urea)\n"
        "Phosphorus: 50 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 50 kg/ha (e.g., MOP)\n"
        "Apply as basal and top dressing."
    ),
    "jute": (
        "Nitrogen: 60 kg/ha (e.g., Urea)\n"
        "Phosphorus: 30 kg/ha (e.g., SSP/DAP)\n"
        "Potassium: 30 kg/ha (e.g., MOP)\n"
        "Split into basal and top dressing."
    ),
    "coffee": (
        "Nitrogen: 120 kg/ha (e.g., Urea)\n"
        "Phosphorus: 90 kg/ha (e.g., DAP)\n"
        "Potassium: 120 kg/ha (e.g., MOP)\n"
        "Split into 2–3 doses per year."
    ),
}

def get_fertilizer_recommendation(crop):
    return fertilizer_data.get(crop.lower(), "Generic recommendation: Urea: 45kg/ha, DAP: 20kg/ha")

#  Session State Setup 
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

#  Optional Location Autofill

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

#  Show Results ONLY if Clicked 

if st.session_state.show_location_result:
    if st.session_state.location_name:
        st.success(f"📍 You are in: **{st.session_state.location_name}**")
    if st.session_state.weather_message:
        st.info(st.session_state.weather_message)
    if st.session_state.weather_error:
        st.error(st.session_state.weather_error) 

#  Inputs Section with Farmer Photos on Both Sides 

st.subheader("🧪 Enter Soil and Weather Data")

left_col, center_col, right_col = st.columns([1, 5, 1])

with left_col:
    st.image(
        "malefarmer.jpeg", 
        caption="Male Farmer",
        use_column_width=True
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
    st.image(
        "femalefarmer.jpeg", 
        caption="Female Farmer",
        use_column_width=True
    )

#  Prediction Button

if st.button("Predict Crop"):
    try:
        model = joblib.load("crop_recommendation_model.pkl")
        scaler = joblib.load("scaler.pkl")
        user_input = scaler.transform([[N, P, K, temperature, humidity, ph, rainfall]])
        pred = model.predict(user_input)[0]
        
        st.success(f"🌱 Recommended Crop: **{pred.upper()}**")

        # Show fertilizer recommendation
        recommendation = get_fertilizer_recommendation(pred)
        st.info(f"🧪 Fertilizer Recommendation:\n{recommendation}")

    except Exception as e:
        st.error(f"⚠️ Something went wrong with prediction: {e}")

from streamlit_geolocation import streamlit_geolocation
import streamlit as st
import requests
import joblib

# Page Setup
st.set_page_config(page_title="Crop Recommender", page_icon="🌾", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .stApp {
        background-color: black;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        color: black;
    }
    .stButton > button {
        background-color: #e63946;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #d62828;
    }
    h1, h2, h3, h4 {
        color: #f1f1f1;
    }
    .caption, .css-10trblm, .css-1v0mbdj, .css-1fv8s86 {
        color: #cccccc;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🌾 Crop Recommendation System")

# API Key
api_key = "d56fb2ef217db80dee4a005b2c8e25e4"

# Helpers
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
        headers = {"User-Agent": "crop-recommender/1.0 (your_email@example.com)"}
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        res = requests.get(url, headers=headers).json()
        return res.get("display_name", "Unknown Location")
    except:
        return "Unknown Location"

# Fertilizer recommendations
fertilizer_data = {
    "rice": "Urea: 50kg/ha, DAP: 25kg/ha",
    "wheat": "Urea: 40kg/ha, DAP: 20kg/ha",
    "maize": "Urea: 55kg/ha, MOP: 20kg/ha",
    "cotton": "Urea: 60kg/ha, SSP: 30kg/ha",
    "sugarcane": "Urea: 80kg/ha, DAP: 40kg/ha, MOP: 30kg/ha",
}
def get_fertilizer_recommendation(crop):
    return fertilizer_data.get(crop.lower(), "Generic recommendation: Urea: 45kg/ha, DAP: 20kg/ha")

# Session State
if "weather_data" not in st.session_state:
    st.session_state.weather_data = {"temp": 0.0, "humidity": 0.0, "rainfall": 0.0}
if "show_location_result" not in st.session_state:
    st.session_state.show_location_result = False
if "location_name" not in st.session_state:
    st.session_state.location_name = None
if "weather_message" not in st.session_state:
    st.session_state.weather_message = None
if "weather_error" not in st.session_state:
    st.session_state.weather_error = None

# Layout
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📍 Optional Weather Auto-fill")
        cols = st.columns([8, 1])
        with cols[0]:
            st.caption("Click to use your location for autofill:")
        with cols[1]:
            clicked = streamlit_geolocation()
        st.markdown('</div>', unsafe_allow_html=True)

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

    # ONLY show after click
    if st.session_state.show_location_result:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.session_state.location_name:
                st.success(f"📍 You are in: **{st.session_state.location_name}**")
            if st.session_state.weather_message:
                st.info(st.session_state.weather_message)
            if st.session_state.weather_error:
                st.error(st.session_state.weather_error)
            st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧪 Enter Soil and Weather Data")
        N = st.number_input("Nitrogen", min_value=0)
        P = st.number_input("Phosphorus", min_value=0)
        K = st.number_input("Potassium", min_value=0)
        temperature = st.number_input("Temperature (°C)", value=st.session_state.weather_data["temp"])
        humidity = st.number_input("Humidity (%)", value=st.session_state.weather_data["humidity"])
        ph = st.number_input("pH", min_value=0.0, max_value=14.0)
        rainfall = st.number_input("Rainfall (mm)", value=st.session_state.weather_data["rainfall"])
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if st.button("Predict Crop"):
            try:
                model = joblib.load("crop_recommendation_model.pkl")
                pred = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])[0]
                st.success(f"🌱 Recommended Crop: **{pred.upper()}**")
                recommendation = get_fertilizer_recommendation(pred)
                st.info(f"🧪 Fertilizer Recommendation:\n{recommendation}")
            except Exception as e:
                st.error(f"⚠️ Something went wrong with prediction: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div style="padding: 10px; background-color: black;">', unsafe_allow_html=True)
    st.image(
        "https://images.unsplash.com/photo-1598970434795-0c54fe7c0642",
        use_column_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


import streamlit as st
import joblib
import numpy as np

# Load the model
try:
    model = joblib.load('crop_recommendation_model.pkl')
except FileNotFoundError:
    st.error("❌ Model file not found! Please make sure 'crop_recommendation_model.pkl' is in the same directory.")
    st.stop()

# Streamlit UI
st.set_page_config(page_title="Crop Recommendation System", page_icon="🌾")
st.title("🌾 Crop Recommendation System")
st.write("Enter the values below to get crop recommendation:")

# Input fields
N = st.number_input("Nitrogen (N)", min_value=0, max_value=140,  step=1)
P = st.number_input("Phosphorus (P)", min_value=5, max_value=145, step=1)
K = st.number_input("Potassium (K)", min_value=5, max_value=205, step=1)
temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=50.0)
humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0)
ph = st.number_input("pH", min_value=3.5, max_value=9.5)
rainfall = st.number_input("Rainfall (mm)", min_value=20.0, max_value=300.0)

# Prediction
if st.button("Recommend Crop",type="primary"):
    try:
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        prediction = model.predict(input_data)
        st.success(f"🌿 Recommended Crop: *{prediction[0].capitalize()}*")
    except Exception as e:
        st.error(f"An error occurred during prediction: {str(e)}")

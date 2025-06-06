
import streamlit as st
import joblib
import numpy as np

model = joblib.load('crop_recommendation_model.pkl')

st.title("🌾 Crop Recommendation System")

st.write("Enter the values below to get crop recommendation:")

N = st.number_input("Nitrogen (N)", 0, 140, step=1)
P = st.number_input("Phosphorus (P)", 5, 145, step=1)
K = st.number_input("Potassium (K)", 5, 205, step=1)
temperature = st.number_input("Temperature (°C)", 0.0, 50.0)
humidity = st.number_input("Humidity (%)", 0.0, 100.0)
ph = st.number_input("pH", 3.5, 9.5)
rainfall = st.number_input("Rainfall (mm)", 20.0, 300.0)


if st.button("Recommend Crop"):
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    prediction = model.predict(input_data)
    st.success(f"🌿 Recommended Crop: **{prediction[0].capitalize()}**")

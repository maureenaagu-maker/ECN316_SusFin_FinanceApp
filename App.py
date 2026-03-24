import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
st.title("Portfolio Optimizer")
# Sidebar inputs
st.sidebar.header("Asset Data")
r_1 = st.sidebar.number_input("Asset 1 Expected Return (%)",
value=5.0) / 100
sd_1 = st.sidebar.number_input("Asset 1 Standard Deviation (%)",
value=9.0) / 100
r_2 = st.sidebar.number_input("Asset 2 Expected Return (%)",
value=12.0) / 100
sd_2 = st.sidebar.number_input("Asset 2 Standard Deviation (%)",
value=20.0) / 100
rho = st.sidebar.number_input("Correlation",
min_value=-1.0, max_value=1.0, value=-0.2)
r_f = st.sidebar.number_input("Risk-Free Rate (%)",
value=2.0) / 100
st.sidebar.header("Your Preferences")
gamma = st.sidebar.slider("Risk Aversion (gamma)",
min_value=0.1, max_value=10.0, value=5.0, step=0.1)

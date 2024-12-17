import streamlit as st
import pandas as pd
from datetime import datetime
import page_dashboard
import page_inbound
import page_outbound
import page_add_sku

# Page configuration
st.set_page_config(page_title="DGM - Warehouse Management System", 
                   page_icon="📊", 
                   layout="wide")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Simple login system
USER_CREDENTIALS = {"Diego": "3333", "Santiago": "1111"}

def login(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        return True
    return False

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'theme' not in st.session_state:
    st.session_state.theme = "dark-mode"

# Theme toggle
def toggle_theme():
    st.session_state.theme = "light-mode" if st.session_state.theme == "dark-mode" else "dark-mode"

# Apply theme
st.markdown(f'<style>body {{ background-color: inherit; }}</style>', unsafe_allow_html=True)
st.markdown(f'<div class="{st.session_state.theme}">', unsafe_allow_html=True)

# Login form
if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Rerun the script to go to the logged-in state
        else:
            st.error("Invalid username or password")
else:
    # Logged-in status
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Record Inbound", "Record Outbound", "Add SKU"])

    # Theme toggle button
    if st.sidebar.button("Toggle Theme"):
        toggle_theme()
        st.rerun()

    # Load the selected page
    if page == "Dashboard":
        page_dashboard.show_page_dashboard()
    elif page == "Record Inbound":
        page_inbound.show_page_inbound()
    elif page == "Record Outbound":
        page_outbound.show_page_outbound()
    elif page == "Add SKU":
        page_add_sku.show_page_add_sku()

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()  # Rerun the script to go back to the login page

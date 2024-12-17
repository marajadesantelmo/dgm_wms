import streamlit as st
import pandas as pd
from datetime import datetime
import page_dashboard
import page_inbound
import page_outbound
import page_add_sku
from io import BytesIO

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

# Function to convert DataFrame to Excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

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

    # Load the selected page
    if page == "Dashboard":
        df = page_dashboard.show_page_dashboard()
    elif page == "Record Inbound":
        df = page_inbound.show_page_inbound()
    elif page == "Record Outbound":
        df = page_outbound.show_page_outbound()
    elif page == "Add SKU":
        df = page_add_sku.show_page_add_sku()

    # Download button
    if df is not None:
        st.sidebar.download_button(
            label="Download data as Excel",
            data=to_excel(df),
            file_name='data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()  # Rerun the script to go back to the login page

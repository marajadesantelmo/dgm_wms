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

# Logged-in state
#st.sidebar.title(f"Welcome, {st.session_state.username}!")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Record Inbound", "Record Outbound", "Add SKU"])

# Load the selected page
if page == "Dashboard":
    page_dashboard.show_page_dashboard()
elif page == "Record Inbound":
    page_inbound.show_page_inbound()
elif page == "Record Outbound":
    page_outbound.show_page_outbound()
elif page == "Add SKU":
    page_add_sku.show_page_add_sku()


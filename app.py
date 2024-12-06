import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
import page_dashboard
import page_inbound
import page_outbound
import page_client

# Page configuration
st.set_page_config(page_title="DGM - Warehouse Management System", 
                   page_icon="📊", 
                   layout="wide")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


current_date = datetime.now().strftime("%Y-%m-%d")
# Sidebar Navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Dashboard", "Record Inbound", "Record Outbound", "Add Client"])

# Dashboard Page
if page == "Dashboard":
    page_dashboard.show_page_dashboard()

elif page == "Record Inbound":
    page_inbound.show_page_inbound()
 
elif page == "Record Outbound":
    page_outbound.show_page_outbound()
    
elif page == "Add Client":
    page_client.show_page_client()
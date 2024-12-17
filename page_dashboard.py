import streamlit as st
import pandas as pd
from supabase_connection import supabase_client, fetch_table_data
from utils import current_stock_table, generate_inbound_table, generate_outbound_table
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_dashboard():
    col1, col2 = st.columns([7, 1])
    with col1:
        st.title("DGM - Warehouse Management System")
        st.subheader("For HBG Supply LLC")
    with col2:
        st.image("logo.png", use_container_width=True)   ## Cambiar a container_withd para pasarlo a cloud
    st.markdown(
        """
        <hr style="border: 1px solid darkgreen; margin-top: 20px; margin-bottom: 20px;">
        """,
        unsafe_allow_html=True)
    # Fetch and display data from Supabase
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    current_stock = current_stock_table(stock, skus)

    #clients = clients[['client_id', 'Name', 'Phone', 'email']]

    inbound = fetch_table_data('inbound')
    inbound_table = generate_inbound_table(inbound, skus)

    outbound = fetch_table_data('outbound')
    outbound_table = generate_outbound_table(outbound, skus)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Current Stock")
        st.dataframe(current_stock, hide_index=True)

    with col2:
        st.subheader("Inbound to Stock")
        st.dataframe(inbound_table, hide_index=True)
    with col3:
        st.subheader("Outbound from Stock")
        st.dataframe(outbound_table, hide_index=True)
    
    return current_stock, inbound_table, outbound_table

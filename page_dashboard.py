import streamlit as st
import pandas as pd
from supabase_connection import supabase_client, fetch_table_data
from utils import current_stock_table
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_dashboard():
    col1, col2 = st.columns([7, 1])
    with col1:
        st.title("DGM - Warehouse Management System")
    with col2:
        st.image("logo.png", use_column_width=True)
    
    # Fetch and display data from Supabase
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    current_stock = current_stock_table(stock, clients, skus)

    clients = clients[['client_id', 'Name', 'Phone', 'email']]

    inbound = fetch_table_data('inbound')
    inbound = inbound.merge(skus, on = 'sku_id')
    inbound['Total Length'] = inbound['Quantity'] * inbound['Length']
    inbound = inbound[['Date', 'Container', 'SKU', 'Quantity', 'Total Length']]

    outbound = fetch_table_data('outbound')
    outbound = outbound.merge(skus, on = 'sku_id')
    outbound['Total Length'] = outbound['Quantity'] * outbound['Length']
    outbound = outbound[['Date', 'Invoice Number', 'SKU', 'Quantity', 'Total Length']]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Current Stock")
        st.dataframe(current_stock, hide_index=True)

    with col2:
        st.subheader("Inbound to Stock")
        st.dataframe(inbound, hide_index=True)
    with col3:
        st.subheader("Outbound from Stock")
        st.dataframe(outbound, hide_index=True)
    
    st.subheader("Clients")
    st.dataframe(clients, hide_index=True)

import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from utils import current_stock_table
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_inbound():
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')

    st.title("Record Inbound")

    # Form to record inbound stock
    with st.form("add_stock_form"):
        container = st.text_input("Container")
        client_name = st.selectbox("Client Name", clients['Name'])
        sku = st.selectbox("SKU", skus['SKU'])
        quantity = st.number_input("Quantity", min_value=1)

        submitted = st.form_submit_button("Record Inbound")

        if submitted:
            # Get client and SKU IDs
            client_id = int(clients.loc[clients['Name'] == client_name, 'client_id'].values[0])
            sku_id = int(skus.loc[skus['SKU'] == sku, 'sku_id'].values[0])

            # Check if stock already exists for the given SKU and client
            existing_stock = stock.loc[(stock['sku_id'] == sku_id) & (stock['client_id'] == client_id)]

            if not existing_stock.empty:
                # Update existing stock quantity
                existing_quantity = int(existing_stock['Quantity'].values[0])
                new_quantity = existing_quantity + quantity
                supabase_client.from_("stock").update({"Quantity": new_quantity}).match({
                    "sku_id": sku_id, "client_id": client_id
                }).execute()
            else:
                # Insert new stock record
                supabase_client.from_("stock").insert([{
                    "sku_id": sku_id, "client_id": client_id, "Quantity": quantity
                }]).execute()

            # Record the inbound transaction
            supabase_client.from_("inbound").insert([{
                "Container": container, "sku_id": sku_id, "client_id": client_id,
                "Date": current_date, "Quantity": quantity
            }]).execute()

            st.success("Inbound record added successfully!")
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
        
        col1, col2 = st.columns(2)

        with col1:
            sku = st.selectbox("1. SKU", skus['SKU'])
            sku2 = st.selectbox("2. SKU", skus['SKU'])
            sku3 = st.selectbox("3. SKU", skus['SKU'])
            sku4 = st.selectbox("4. SKU", skus['SKU'])
            sku5 = st.selectbox("5. SKU", skus['SKU'])
            sku6 = st.selectbox("6. SKU", skus['SKU'])
            sku7 = st.selectbox("7. SKU", skus['SKU'])
            sku8 = st.selectbox("8. SKU", skus['SKU'])
            sku9 = st.selectbox("9. SKU", skus['SKU'])
            sku10 = st.selectbox("10. SKU", skus['SKU'])

        with col2:
            quantity = st.number_input("Quantity item 1", min_value=1)
            quantity2 = st.number_input("Quantity item 2", min_value=1)
            quantity3 = st.number_input("Quantity item 3", min_value=1)
            quantity4 = st.number_input("Quantity item 4", min_value=1)
            quantity5 = st.number_input("Quantity item 5", min_value=1)
            quantity6 = st.number_input("Quantity item 6", min_value=1)
            quantity7 = st.number_input("Quantity item 7", min_value=1)
            quantity8 = st.number_input("Quantity item 8", min_value=1)
            quantity9 = st.number_input("Quantity item 9", min_value=1)
            quantity10 = st.number_input("Quantity item 10", min_value=1)

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
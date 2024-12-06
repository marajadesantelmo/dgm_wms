import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
from utils import get_next_outbound_id

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_outbound():
    st.title("Record Outbound")
    
    # Fetch and prepare data
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    stock = stock.merge(clients[['client_id', 'Name']], on='client_id')
    stock = stock.merge(skus, on='sku_id')

    # Form to delete stock and record outbound
    with st.form("delete_stock_form"):
        # Create options for selection
        stock_options = [
            f"{row['sku_id']}: {row['SKU']}" for _, row in stock.iterrows()
        ]
        client_name = st.selectbox("Client Name", clients['Name'])
        selected_stock = st.selectbox("Select Stock to Record Outbound", stock_options)
        quantity = st.number_input("Quantity to Subtract", min_value=1)
        submitted = st.form_submit_button("Record Outbound")
        
        if submitted:
            # Extract stock and client details
            sku_id = int(selected_stock.split(": ")[0])
            client_id = int(clients.loc[clients['Name'] == client_name, 'client_id'].values[0])

            # Check if stock already exists for the given sku_id and client_id
            existing_stock = stock.loc[(stock['sku_id'] == sku_id) & (stock['client_id'] == client_id)]

            if existing_stock.empty:
                st.error("No stock available for the selected SKU and Client.")
            
            else:
                current_quantity = stock.loc[
                    (stock['sku_id'] == sku_id) & (stock['client_id'] == client_id),
                    'Quantity'
                ].values[0]

                # Check for sufficient stock
                if quantity > current_quantity:
                    st.error("The quantity to subtract exceeds the current stock quantity.")
                else:
                    # Calculate the new stock quantity
                    new_quantity = current_quantity - quantity
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Update stock in Supabase
                    update_response = supabase_client.from_("stock").update({
                        "Quantity": int(new_quantity)
                    }).match({
                        "sku_id": sku_id,
                        "client_id": client_id
                    }).execute()
                    
                    if update_response.data:
                        st.success(
                            f"Outbound record created successfully! Remaining stock: {new_quantity}"
                        )
                        outbound_id = get_next_outbound_id()
                        outbound_response = supabase_client.from_("outbound").insert([{
                            'id': int(outbound_id),
                            "sku_id": sku_id,
                            "client_id": client_id,
                            "Date": current_date,
                            "Quantity": int(quantity)
                        }]).execute()

                    else:
                        st.error("Failed to update stock.")
    # Display current stock
    st.subheader("Current Stock")
    st.dataframe(stock[['sku_id', 'SKU', 'Name', 'Quantity']], hide_index=True)
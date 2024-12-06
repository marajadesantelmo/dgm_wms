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

    # Form to record outbound stock by invoice number
    with st.form("record_outbound_form"):
        client_name = st.selectbox("Client Name", clients['Name'])
        invoice = st.text_input("Invoice Number")

        col1, col2 = st.columns(2)

        # Grouping SKUs by invoice number
        with col1:
            # Selectbox for up to 10 SKUs, default value set to None or "" to prevent accidental selection
            skus_selected = [
                st.selectbox(f"{i+1}. SKU", [""] + skus['SKU'].tolist(), key=f"sku_{i}")
                for i in range(10)
            ]

        with col2:
            # Number inputs for quantities of up to 10 items
            quantities = [
                st.number_input(f"Quantity item {i+1}", min_value=1, key=f"qty_{i}")
                for i in range(10)
            ]

        submitted = st.form_submit_button("Record Outbound")

        if submitted:
            # Filter out items where SKU is empty or quantity is 0
            outbound_data = []
            for i in range(10):
                if skus_selected[i] and quantities[i] > 0:
                    sku_id = int(skus.loc[skus['SKU'] == skus_selected[i], 'sku_id'].values[0])
                    quantity = quantities[i]

                    # Get client_id
                    client_id = int(clients.loc[clients['Name'] == client_name, 'client_id'].values[0])

                    # Check if stock already exists for the given SKU and client
                    existing_stock = stock.loc[(stock['sku_id'] == sku_id) & (stock['client_id'] == client_id)]

                    if existing_stock.empty:
                        st.error(f"No stock available for SKU {skus_selected[i]} and Client {client_name}.")
                    else:
                        current_quantity = int(existing_stock['Quantity'].values[0])

                        # Check for sufficient stock
                        if quantity > current_quantity:
                            st.error(f"The quantity to subtract exceeds the current stock for SKU {skus_selected[i]}.")
                        else:
                            # Calculate the new stock quantity
                            new_quantity = current_quantity - quantity

                            # Update stock in Supabase
                            update_response = supabase_client.from_("stock").update({
                                "Quantity": new_quantity
                            }).match({
                                "sku_id": sku_id,
                                "client_id": client_id
                            }).execute()

                            if update_response.data:
                                outbound_data.append({
                                    'sku_id': sku_id,
                                    'client_id': client_id,
                                    'Date': current_date,
                                    'Quantity': quantity,
                                    'Invoice Number': invoice
                                })
                            else:
                                st.error("Failed to update stock.")
            
            # Insert outbound records in batch if there are valid items
            if outbound_data:
                outbound_id = get_next_outbound_id()
                for record in outbound_data:
                    record['id'] = int(outbound_id)
                    outbound_response = supabase_client.from_("outbound").insert([record]).execute()

                    if outbound_response.data:
                        st.success(f"Outbound record for Invoice {invoice} created successfully!")
                    else:
                        st.error(f"Failed to create outbound record for SKU {record['sku_id']}.")
            else:
                st.warning("No valid items selected or quantities exceed available stock.")

    # Display current stock
    st.subheader("Current Stock")
    st.dataframe(stock[['sku_id', 'SKU', 'Name', 'Quantity']], hide_index=True)
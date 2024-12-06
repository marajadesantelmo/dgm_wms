import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
#import page_dashboard
import page_inbound
#import page_outbound
#import page_clients

            
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

page = st.sidebar.radio("Go to", ["Dashboard", "Record Inbound", "Record Outbound", "Record Inbound"])

# Dashboard Page
if page == "Dashboard":

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
    inbound = inbound.merge(clients[['client_id', 'Name']], on='client_id')
    inbound = inbound[['Date', 'Name', 'SKU', 'Quantity']]

    outbound = fetch_table_data('outbound')
    outbound = outbound.merge(skus, on = 'sku_id')
    outbound = outbound.merge(clients[['client_id', 'Name']], on='client_id')
    outbound = outbound[['Date', 'Name', 'SKU', 'Quantity']]

    st.subheader("Current Stock")
    st.dataframe(current_stock, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Inbound to Stock")
        st.dataframe(inbound, hide_index=True)

    with col2:
        st.subheader("Outbound from Stock")
        st.dataframe(outbound, hide_index=True)
    
    st.subheader("Clients")
    st.dataframe(clients, hide_index=True)

# Add Stock Page
elif page == "Record Inbound":
    page_inbound.show_page_inbound()
 

# Record Outbound Page
elif page == "Record Outbound":
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
# Add Client Page
elif page == "Add Client":
    st.title("Add Client")
    
    # Form to add new client
    with st.form("add_client_form"):
        client_name = st.text_input("Client Name")
        contact = st.text_input("Contact")
        email = st.text_input("e-mail")
        
        submitted = st.form_submit_button("Add Client")
        
        if submitted:
            id= int(get_next_client_id())
            client_response = supabase_client.from_("clients").insert({
                "Name": client_name,
                "Phone": contact,
                "email": email,
                "client_id": id
            }).execute()
            
            if client_response.data:
                st.success("Client added successfully!")
            else:
                st.error("Failed to add client.")
import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client

# Helper function to get the next client ID
def get_next_client_id():
    clients = fetch_table_data('clients')
    if clients.empty:
        return 1
    else:
        return clients['client_id'].max() + 1

# Helper function to get the next item ID
def get_next_inbound_id():
    inbound = fetch_table_data('inbound')
    return inbound['id'].max() + 1

# Helper function to get available client IDs
def get_available_client_ids():
    clients = fetch_table_data('clients')
    return clients['client_id'].tolist() if not clients.empty else []

# Helper function to get available clients
def get_available_clients():
    clients = fetch_table_data('clients')
    if not clients.empty:
        return clients[['client_id', 'Name']].to_dict('records')
    return []

def current_stock_table(stock, clients, skus):
    stock = stock.merge(clients[['client_id', 'Name']], on='client_id')
    stock = stock.merge(skus, on = 'sku_id')
    stock.drop(columns=['sku_id', 'client_id'], inplace=True)
    stock.rename(columns={'Name': 'Client Name'}, inplace=True)
    current_stock = stock[['Client Name', 'SKU', 'quantity']]
    return current_stock


# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Stock", "Record Outbound", "Add Client"])

# Dashboard Page
if page == "Dashboard":

    col1, col2 = st.columns([1, 7])
    with col1:
        st.image("logo.png", use_container_width=True)
    with col2:
        st.title("Warehouse Management System")
    
    # Fetch and display data from Supabase
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    current_stock = current_stock_table(stock, clients, skus)

    inbound = fetch_table_data('inbound')
    inbound = inbound.merge(skus, on = 'sku_id')
    inbound = inbound[['Date', 'SKU', 'quantity']]

    st.subheader("Current Stock")
    st.dataframe(current_stock, hide_index=True)

    st.subheader("Inbound to Stock")
    st.dataframe(inbound, hide_index=True)
    
    st.subheader("Clients")
    st.dataframe(clients, hide_index=True)

    


# Add Stock Page
elif page == "Add Stock":
    st.title("Add Stock")
    
    # Fetch available clients
    clients = fetch_table_data('clients')
    skus = fetch_table_data('skus')
    
    # Form to add new stock
    with st.form("add_stock_form"):
        sku = st.selectbox("SKU", skus['SKU'])
        client_name = st.selectbox("Client Name", clients['Name'] )
        quantity = st.number_input("Quantity", min_value=1)
        submitted = st.form_submit_button("Add Stock")
        
        if submitted:
            # Get ids
            client_id = int(clients.loc[clients['Name'] == client_name, 'client_id'].values[0])
            sku_id = int(skus.loc[skus['SKU'] == sku, 'sku_id'].values[0])
            id = int(get_next_inbound_id())
            
            # Insert new inbound entry into Supabase
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            inbound_response = supabase_client.from_("inbound").insert([{
                "id": id,
                "Date": current_date,
                "sku_id": sku_id,
                "quantity": quantity
            }]).execute()
            
            if inbound_response.data:
                # Insert new stock entry into Supabase
                stock_response = supabase_client.from_("stock").insert([{
                    "sku_id": sku_id,
                    "client_id": client_id,
                    "quantity": quantity,
                }]).execute()
                
                if stock_response.data:
                    st.success("Stock added successfully!")
                else:
                    st.error("Failed to add stock.")
            else:
                st.error("Failed to add inbound entry.")

# Record Outbound Page
elif page == "Record Outbound":
    st.title("Record Outbound")
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    stock = stock.merge(clients[['client_id', 'Name']], on='client_id')
    stock = stock.merge(skus, on = 'sku_id')
    # Form to delete stock and record outbound
    with st.form("delete_stock_form"):

        stock_ids = stock['sku_id'].tolist()
        stock_skus = stock['SKU'].tolist()
        stock_options = [f"{stock_id}: {desc}" for stock_id, desc in zip(stock_ids, stock_skus)]

        clients_options = [f"{client_id}: {name}" for client_id, name in zip(clients['client_id'], clients['Name'])]
        
        selected_stock = st.selectbox("Select Stock to Record Outbound", stock_options)
        selected_client = st.selectbox("Select Client", clients_options)
        quantity = st.number_input("Quantity", min_value=1)
        submitted = st.form_submit_button("Record Outbound")
        
        if submitted:
            # Extract the selected stock ID
            stock_id_to_delete = int(selected_stock.split(": ")[0])
            client_id = int(selected_client.split(": ")[0])
            current_quantity = stock.loc[(stock['id'] == stock_id_to_delete) & (stock['client_id'] == client_id), 'quantity'].values[0]
            new_quantity = current_quantity - quantity
            
            if new_quantity < 0:
                st.error("The quantity to subtract exceeds the current stock quantity.")

            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Insert new outbound entry into Supabase
            outbound_response = supabase_client.from_("outbound").insert([{
                "id": stock_id_to_delete,
                "Date": current_date,
                "Quantity": quantity
            }]).execute()
            
            if outbound_response.data:
                # Delete stock from Supabase
                update_response = supabase_client.from_("stock").update({
                        "quantity": new_quantity
                    }).eq("id", stock_id_to_delete).execute()
                if update_response.data:
                    st.success("Stock recorded as outbound and deleted successfully!")
                else:
                    st.error("Failed to delete stock.")
            else:
                st.error("Failed to record outbound.")

        # Display stock data
    st.subheader("Current Stock")
    st.dataframe(stock, hide_index=True)

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
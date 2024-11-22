import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client

# Helper function to get the next client ID
def get_next_client_id():
    clients_df = fetch_table_data('clients')
    if clients_df.empty:
        return 1
    else:
        return clients_df['id'].max() + 1

# Helper function to get the next item ID
def get_next_item_id():
    clients_df = fetch_table_data('inbound')
    if clients_df.empty:
        return 1
    else:
        return clients_df['id'].max() + 1

# Helper function to get available client IDs
def get_available_client_ids():
    clients_df = fetch_table_data('clients')
    return clients_df['id'].tolist() if not clients_df.empty else []

# Helper function to get available clients
def get_available_clients():
    clients_df = fetch_table_data('clients')
    if not clients_df.empty:
        return clients_df[['id', 'name']].to_dict('records')
    return []

# Add logo to the top


# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Stock", "Delete Stock", "Add Client"])

# Dashboard Page
if page == "Dashboard":

    col1, col2 = st.columns([1, 7])
    with col1:
        st.image("logo.png", use_column_width=True)
    with col2:
        st.title("Warehouse Management System")
    
    # Fetch and display data from Supabase
    clients_df = fetch_table_data('clients')
    stock_df = fetch_table_data('stock')
    inbound_df = fetch_table_data('inbound')
    outbound_df = fetch_table_data('outbound')
    
    st.subheader("Clients")
    st.dataframe(clients_df, hide_index=True)
    
    st.subheader("Stock")
    st.dataframe(stock_df, hide_index=True)
    
    st.subheader("Inbound")
    st.dataframe(inbound_df, hide_index=True)
    
    st.subheader("Outbound")
    st.dataframe(outbound_df, hide_index=True)

# Add Stock Page
elif page == "Add Stock":
    st.title("Add Stock")
    
    # Fetch available clients
    available_clients = get_available_clients()
    client_names = [client['name'] for client in available_clients]
    
    # Form to add new stock
    with st.form("add_stock_form"):
        description = st.text_input("Description")
        client_name = st.selectbox("Client Name", client_names)
        quantity = st.number_input("Quantity", min_value=1)
        measure = st.text_input("Measure")
        sku1 = st.text_input("SKU1")
        sku2 = st.text_input("SKU2")
        submitted = st.form_submit_button("Add Stock")
        
        if submitted:
            # Get the client ID based on the selected client name
            client_id = next(client['id'] for client in available_clients if client['name'] == client_name)
            id = int(get_next_item_id()) 
            
            # Insert new inbound entry into Supabase
            inbound_response = supabase_client.from_("inbound").insert([{
                "id": id,
            }]).execute()

            outbound_response = supabase_client.from_("outbound").insert([{
                "id": id,
                "date": "2030-01-01 00:00:00+00"
            }]).execute()
            
            if inbound_response.data:
                # Insert new stock entry into Supabase
                stock_response = supabase_client.from_("stock").insert([{
                    "id": id,
                    "inbound": id,
                    "description": description,
                    "client": client_id,
                    "quantity": quantity,
                    "measure": measure,
                    "sku1": sku1,
                    "sku2": sku2
                }]).execute()
                
                if stock_response.data:
                    st.success("Stock added successfully!")
                else:
                    st.error("Failed to add stock.")
            else:
                st.error("Failed to add inbound entry.")

# Delete Stock Page
elif page == "Delete Stock":
    st.title("Delete Stock")
    
    # Form to delete stock
    with st.form("delete_stock_form"):
        stock_id = st.number_input("Stock ID to delete", min_value=1)
        
        submitted = st.form_submit_button("Delete Stock")
        
        if submitted:
            # Delete stock from Supabase
            supabase_client.from_("stock").delete().eq("id", stock_id).execute()
            st.success("Stock deleted successfully!")

# Add Client Page
elif page == "Add Client":
    st.title("Add Client")
    
    # Form to add new client
    with st.form("add_client_form"):
        client_name = st.text_input("Client Name")
        contact = st.text_input("Contact")
        
        submitted = st.form_submit_button("Add Client")
        
        if submitted:
            # Insert new client into Supabase
            client_response = supabase_client.from_("clients").insert({
                "name": client_name,
                "contact": contact,
                "added": pd.Timestamp.now().isoformat()
            }).execute()
            
            if client_response.data:
                st.success("Client added successfully!")
            else:
                st.error("Failed to add client.")
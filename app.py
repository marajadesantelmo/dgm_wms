import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
            
# Page configuration
st.set_page_config(page_title="DGM - Warehouse Management System", 
                   page_icon="📊", 
                   layout="wide")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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

def get_next_outbound_id():
    inbound = fetch_table_data('outbound')
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
    current_stock = stock[['Client Name', 'SKU', 'Quantity']]
    return current_stock

current_date = datetime.now().strftime("%Y-%m-%d")
# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Record Inbound", "Record Outbound", "Add Client"])

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

    
# Record Inbound Page
elif page == "Record Inbound":
    clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')

    if "items" not in st.session_state:
        st.session_state.items = [{"SKU": "", "Quantity": 1}]

    def add_item():
        st.session_state.items.append({"SKU": "", "Quantity": 1})

    def remove_item():
        if len(st.session_state.items) > 1:
            st.session_state.items.pop()

    st.title("Record Inbound")

    # Form to add new stock
    with st.form("add_stock_form"):
        container = st.text_input("Container")
        client_name = st.selectbox("Client Name", clients['Name'])
        
        st.write("Items:")
        for idx, item in enumerate(st.session_state.items):
            col1, col2 = st.columns(2)
            with col1:
                item["SKU"] = st.selectbox(f"SKU {idx + 1}", skus['SKU'], key=f"sku_{idx}")
            with col2:
                item["Quantity"] = st.number_input(f"Quantity {idx + 1}", min_value=1, key=f"quantity_{idx}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("Add Item", on_click=add_item)
        with col2:
            st.button("Remove Item", on_click=remove_item)

        submitted = st.form_submit_button("Record Inbound")

    if submitted:
        client_id = int(clients.loc[clients['Name'] == client_name, 'client_id'].values[0])

        for item in st.session_state.items:
            sku_id = int(skus.loc[skus['SKU'] == item["SKU"], 'sku_id'].values[0])
            quantity = item["Quantity"]
            
            # Check if stock already exists for the given sku_id and client_id
            existing_stock = stock.loc[(stock['sku_id'] == sku_id) & (stock['client_id'] == client_id)]
            
            if not existing_stock.empty:
                existing_quantity = int(existing_stock['Quantity'].values[0])
                new_quantity = existing_quantity + quantity
                supabase_client.from_("stock").update({"Quantity": new_quantity}).match({
                    "sku_id": sku_id, "client_id": client_id
                }).execute()
            else:
                supabase_client.from_("stock").insert([{
                    "sku_id": sku_id, "client_id": client_id, "Quantity": quantity
                }]).execute()

            # Record inbound entry
            supabase_client.from_("inbound").insert([{
                "Container": container, "sku_id": sku_id, "client_id": client_id,
                "Date": current_date, "Quantity": quantity
            }]).execute()

        st.success("Inbound records updated successfully!")

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
    st.dataframe(stock[['sku_id', 'SKU', 'Name', 'quantity']], hide_index=True)
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
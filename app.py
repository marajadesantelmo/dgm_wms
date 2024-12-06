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

elif page == "Record Inbound":
    page_inbound.show_page_inbound()
 
elif page == "Record Outbound":
    page_outbound.show_page_outbound()
    

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
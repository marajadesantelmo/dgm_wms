import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
from utils import get_next_outbound_id, generate_outbound_table, current_stock_table, generate_invoice

current_date = datetime.now().strftime("%Y-%m-%d")

def show_page_outbound():
    st.title("Record Outbound")

    # Fetch and prepare data
    #clients = fetch_table_data('clients')
    stock = fetch_table_data('stock')
    skus = fetch_table_data('skus')
    #stock = stock.merge(clients[['client_id', 'Name']], on='client_id')
    outbount = fetch_table_data('outbound')
    outbound_table = generate_outbound_table(outbount, skus)
    current_stock = current_stock_table(stock, skus)

    # Form to record outbound stock by invoice number
    with st.form("record_outbound_form"):
        #client_name = st.selectbox("Client Name", clients['Name'])
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
            # Number inputs for lengths of up to 10 items
            lengths = [
                st.number_input(f"Length item {i+1}", min_value=0, key=f"length_{i}")
                for i in range(10)
            ]

        submitted = st.form_submit_button("Record Outbound")

        if submitted:
            # Filter out items where SKU is empty or quantity is 0
            outbound_data = []
            inovice_data = []
            for i in range(10):
                if skus_selected[i] and lengths[i] > 0:
                    sku_id = int(skus.loc[skus['SKU'] == skus_selected[i], 'sku_id'].values[0])
                    length = lengths[i]

                    # FIJO CLIENT ID
                    #client_id = int(clients.loc[clients['Name'] == client_name, 'client_id'].values[0])
                    client_id = 5
                    
                    existing_stock = stock.loc[(stock['sku_id'] == sku_id) & (stock['client_id'] == client_id)]
                    unit_length = skus.loc[skus['sku_id'] == sku_id, 'Length'].values[0]
                    quantity = int(length / unit_length)

                    if existing_stock.empty:
                        #st.error(f"No stock available for SKU {skus_selected[i]} and Client {client_name}.")
                        st.error(f"No stock available for SKU {skus_selected[i]}")
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

                                inovice_data.append({
                                    'sku_id': sku_id,
                                    'SKU': skus_selected[i],
                                    'Date': current_date,
                                    'Quantity': quantity,
                                    'total_length': length,
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

                pdf = generate_invoice(invoice, outbound_data)
                pdf_output = pdf.output(dest='S').encode('latin1')
                
                # Store the PDF output in session state
                st.session_state.pdf_output = pdf_output
                st.session_state.invoice = invoice
            else:
                st.warning("No valid items selected or lengths exceed available stock.")

    if 'pdf_output' in st.session_state and 'invoice' in st.session_state:
        st.download_button(
            label="Download Invoice",
            data=st.session_state.pdf_output,
            file_name=f"invoice_{st.session_state.invoice}.pdf",
            mime="application/pdf"
        )

    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("Outbound from Stock")
        outbound_table = outbound_table.sort_values(by='Date', ascending=False)
        st.dataframe(outbound_table, hide_index=True)
    with col2:
        # Display current stock
        st.subheader("Current Stock")
        st.dataframe(current_stock, hide_index=True)
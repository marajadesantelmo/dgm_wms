import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, supabase_client
from datetime import datetime
from utils import get_next_outbound_id, generate_outbound_table, current_stock_table, generate_invoice, generate_invoice_outbound_order

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

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.form("record_outbound_form"):
            #client_name = st.selectbox("Client Name", clients['Name'])
            invoice = st.text_input("Invoice Number (please enter only numbers)")
            col1_1, col1_2 = st.columns(2)
            # Grouping SKUs by invoice number
            with col1_1:
                # Selectbox for up to 10 SKUs, default value set to None or "" to prevent accidental selection
                skus_selected = [
                    st.selectbox(f"{i+1}. SKU", [""] + skus['SKU'].tolist(), key=f"sku_{i}")
                    for i in range(10)
                ]

            with col1_2:
                # Number inputs for lengths of up to 10 items
                lengths = [
                    st.number_input(f"Length item {i+1}", min_value=0, key=f"length_{i}")
                    for i in range(10)
                ]

            submitted = st.form_submit_button("Record Outbound")

            if submitted:
                if not invoice.isnumeric():
                    st.error("Invoice Number must be numeric.")
                else:
                    # Filter out items where SKU is empty or quantity is 0
                    outbound_data = []
                    invoice_data = []
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

                                        invoice_data.append({
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
                        #Generate invoice for outbound order
                        pdf = generate_invoice_outbound_order(invoice, invoice_data)
                        pdf_output = pdf.output(dest='S').encode('latin1')
                        st.session_state.pdf_output = pdf_output
                        st.session_state.invoice = invoice
                    else:
                        st.warning("No valid items selected or lengths exceed available stock.")

        if 'pdf_output' in st.session_state and 'invoice' in st.session_state:
            st.download_button(
                label="Download Outbound Order",
                data=st.session_state.pdf_output,
                file_name=f"invoice_{st.session_state.invoice}.pdf",
                mime="application/pdf"
            )
    with col2: 
        st.subheader("Current Stock")
        st.dataframe(current_stock, hide_index=True)
        st.subheader("Validate Outbound Records")
        invoice_numbers = [""] + outbound_table['Invoice Number'].fillna(0).astype(int).tolist()
        selected_invoice = st.selectbox("Select Invoice Number", invoice_numbers)
        if selected_invoice:
            outbound_id = selected_invoice
        else:
            outbound_id = st.text_input("Or enter Invoice Number manually")
        if st.button("Validate Outbound"):
            if outbound_id:
                outbound_validation_response = supabase_client.from_("outbound").update({
                    "Status": "Validated"}).match({"Invoice Number": outbound_id}).execute()
            if outbound_validation_response.data:
                st.success(f"Outbound {outbound_id} has been validated.")
                if 'pdf_output' in st.session_state and 'invoice' in st.session_state:
                    st.download_button(
                        label="Download Invoice",
                        data=st.session_state.pdf_output,
                        file_name=f"invoice_{st.session_state.invoice}.pdf",
                        mime="application/pdf")
            else:
                st.error(f"Failed to validate outbound {outbound_id}.")
    st.subheader("Outbound from Stock")
    outbound_table = outbound_table.sort_values(by='Date', ascending=False)
    st.dataframe(outbound_table, hide_index=True)

    
    # Invoice validation

from supabase_connection import fetch_table_data

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
    outbound = fetch_table_data('outbound')
    return outbound['id'].max() + 1

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

def current_stock_table(stock, skus):
    stock = stock.merge(skus, on = 'sku_id')
    stock.drop(columns=['sku_id', 'client_id'], inplace=True)
    stock.rename(columns={'Name': 'Client Name'}, inplace=True)
    stock['Total Length'] = stock['Quantity'] * stock['Length']
    current_stock = stock[['SKU', 'Lenth', 'Quantity', 'Total Length']]
    return current_stock

def generate_inbound_table(inbound, skus):
    inbound = inbound.merge(skus, on = 'sku_id')
    inbound['Total Length'] = inbound['Quantity'] * inbound['Length']
    inbound = inbound[['Date', 'Container', 'SKU', 'Quantity', 'Total Length']]
    return inbound

def generate_outbound_table(outbound, skus):
    outbound = outbound.merge(skus, on = 'sku_id')
    outbound['Total Length'] = outbound['Quantity'] * outbound['Length']
    outbound = outbound[['Date', 'Invoice Number', 'SKU', 'Quantity', 'Total Length']]
    return outbound
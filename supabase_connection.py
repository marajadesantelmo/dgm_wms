from supabase import create_client, Client
import pandas as pd
import os

url = os.getenv("url_saupabase")
key = os.getenv("key_supabase")

supabase_client = create_client(url, key)

def fetch_table_data(table_name):
    query = (
        supabase_client
        .from_(table_name)
        .select('*')
        .execute()
    )
    return pd.DataFrame(query.data)

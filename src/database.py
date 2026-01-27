from supabase import create_client
import streamlit as st

def process_responses_dict(responses_dict):
    
    output_dict = {}

    for key, value in responses_dict.items():
        if isinstance(value, dict):
            output_dict.update(value)
        else:
            output_dict[key] = value

    output_dict = set_lowercase_keys(output_dict)

    return output_dict

def set_lowercase_keys(input_dict):
    return {k.lower(): v for k, v in input_dict.items()}

def insert_row(row_dict):
    
    # Configurar Supabase
    
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    response = supabase.table("pd_lvp_verano").insert(row_dict).execute()

def send_to_database(responses_dict):

    row_dict = process_responses_dict(responses_dict)

    insert_row(row_dict)

    st.session_state["responses_sent"] = True

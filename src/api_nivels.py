import streamlit as st
from src.directions import get_google_directions

def get_origin():
    lat = st.session_state["responses"]["od_screen"].get("Origen_latitude", None)
    lon = st.session_state["responses"]["od_screen"].get("Origen_longitude", None)
    if lat is not None and lon is not None:
        return (lat, lon)
    else:
        return None

def get_destination():
    lat = st.session_state["responses"]["od_screen"].get("Destino_latitude", None)
    lon = st.session_state["responses"]["od_screen"].get("Destino_longitude", None)
    if lat is not None and lon is not None:
        return (lat, lon)
    else:
        return None
    
def save_api_nivels():
    if "api_nivels" not in st.session_state["responses"]:
        origen = get_origin()
        destino = get_destination()
        liv_nivels_dict = get_google_directions(origen, destino, mode='driving')
        txb_nivels_dict = get_google_directions(origen, destino, mode='transit')
        api_nivels_dict = {**liv_nivels_dict, **txb_nivels_dict}
        st.session_state["responses"]["api_nivels"] = api_nivels_dict
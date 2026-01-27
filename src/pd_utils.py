import streamlit as st
import pandas as pd
import geopandas as gpd

def get_modo_PR():
    modo_PR = st.session_state["responses"]["screen3"].get("modo_PR", False)
    return modo_PR

def get_nivels_PR():

    screen_list = ["screen51", "screen52", "screen53"]
    
    for screen in screen_list:
        if screen in st.session_state["responses"]:
            return st.session_state["responses"][screen]
    
    return None

def get_nivels_api():
    return st.session_state["responses"].get("api_nivels", None)

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

def get_nearest_multiple(x1, x2):
    """
    Retorna el múltiplo de x2 más cercano a x1.
    
    Args:
        x1: Valor de referencia
        x2: Base del múltiplo
    
    Returns:
        El múltiplo de x2 más cercano a x1
    """
    return round(x1 / x2) * x2

### ------------------------------------------
### Función para identificar Nro Diseño
### ------------------------------------------

def identify_nro_disenho(responses_dict):

    pass


### ------------------------------------------
### Función para generar diseño experimental PD
### ------------------------------------------

def generate_choice_set_df(nro_disenho):

    disenhos_df = pd.read_csv("data/disenhos_pd.csv", sep = ";")
    df = disenhos_df[disenhos_df["DIS"] == nro_disenho]
    df.set_index("Tj", inplace=True)

    df_modified = apply_deltas_to_choice_set_df(df)

    return df_modified

def apply_deltas_to_choice_set_df(df):

    df_modified = df.copy()

    delta_c = pd.Series([0,1000,500,2000]*2, index=df.index) 
    delta_tv = pd.Series([0,5,5,0]*2, index=df.index) 

    df_modified["c1"] = df_modified["c1"] + delta_c
    df_modified["tv1"] = df_modified["tv1"] + delta_tv

    df_modified["c2"] = df_modified["c2"] + delta_c
    df_modified["tv2"] = df_modified["tv2"] + delta_tv

    return df_modified

def compute_differences(df):
    df_diff = pd.DataFrame()
    df_diff['delta_c'] = df['c2'] - df['c1']
    df_diff['delta_tv'] = df['tv2'] - df['tv1']
    df_diff['delta_tc'] = df['tc2'] - df['tc1']
    df_diff['delta_te'] = df['te2'] - df['te1']
    return df_diff
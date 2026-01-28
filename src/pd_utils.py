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

def identify_mode(lugar):
    if lugar.startswith("Terminal"):
        return "Bus"
    else: 
        return "Auto Particular"

def uniform_comuna(comuna):

    if comuna == "Licanray":
        return "Pucón"
    
    elif comuna == "Padre las casas":
        return "Temuco"
    
    else: 
        return comuna

def cargar_id_disenhos_df():
    id_disenhos_df = pd.read_csv("data/disenhos.csv", sep=";")
    id_disenhos_df.set_index("DIS", inplace=True)
    return id_disenhos_df

def get_id_disenho(id_disenhos_df, modo, origen, destino):
    filtro = ((id_disenhos_df["Origen"] == origen) &
              (id_disenhos_df["Destino"] == destino) &
                (id_disenhos_df["Modo"] == modo))
    disenhos_filtrados = id_disenhos_df[filtro]

    assert len(disenhos_filtrados) <= 1, "Error: Más de un diseño coincide con los criterios especificados."

    if len(disenhos_filtrados) == 0:
        return 0
    
    return disenhos_filtrados.index[0]

def identify_nro_disenho(responses_dict):

    lugar = responses_dict["screen1"]["lugar_encuesta"]
    modo = identify_mode(lugar)
    origen = uniform_comuna(responses_dict["screen3"]["origen"])
    destino = uniform_comuna(responses_dict["screen3"]["destino"])

    id_disenhos_df = cargar_id_disenhos_df()

    id_disenho_od = get_id_disenho(id_disenhos_df, modo, origen, destino)
    id_disenho_do = get_id_disenho(id_disenhos_df, modo, destino, origen)

    id_disenho = id_disenho_od + id_disenho_do

    return id_disenho

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
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
### Funciones para calcular niveles de servicio PD
### Alternativa Actual (modo_PR)
### ------------------------------------------

def compute_c_pd_current_mode(modo_PR,nivels_PR, nivels_api):

    if modo_PR == "Auto Particular":
        dv_liv = nivels_api["dv_liv"]
        c_bencina = dv_liv * 90 # 90 $/km calculado en base a consumo de 15 km/l y precio de bencina de 1350 $/litro
        c_estacionamiento = nivels_PR["c_liv_PR"]
        c = c_bencina + c_estacionamiento

        if c < 200 * dv_liv + 800:
            if c < 1200:
                c_pd = 1200
            else:
                c_pd = get_nearest_multiple(c, 50)

        else:
            c_pd = get_nearest_multiple(200 * dv_liv + 800, 50)

    elif modo_PR == "Taxibus":
        c_pr = nivels_PR["c_txb_PR"]
        c_pd = 630
    
    elif modo_PR == "Taxicolectivo":
        c_pr = nivels_PR["c_txc_PR"]
        
        dv_liv = nivels_api["dv_liv"]
        c_estimado = dv_liv * 170

        c_pd = get_nearest_multiple((c_pr + c_estimado) / 2, 50)

    c_pd_list = [int(c_pd)] * 8
    return c_pd_list

def compute_tv_pd_current_mode(modo_PR, nivels_PR, nivels_api):

    if modo_PR == "Auto Particular":

        tv_pr = nivels_PR["tv_liv_PR"]
        tv_api = nivels_api["tv_liv"]

    elif modo_PR == "Taxibus":

        tv_pr = nivels_PR["tv_txb_PR"]
        tv_api = nivels_api["tv_txb"]

    elif modo_PR == "Taxicolectivo":
            
        tv_pr = nivels_PR["tv_txc_PR"]
        tv_api = nivels_api["tv_liv"] # La API no tiene tv para taxicolectivo, se usa el de liviano

    tv_pd = int((tv_pr + tv_api) / 2)
    tv_pd_list = [tv_pd] * 8
    return tv_pd_list

def compute_tc_pd_current_mode(modo_PR, nivels_PR, nivels_api):

    if modo_PR == "Auto Particular":

        tc_pr = nivels_PR["tc_liv_PR"]
        tc_pd = min(int(tc_pr),5)

    elif modo_PR == "Taxibus":

        tc_pr = nivels_PR["tca_txb_PR"] + nivels_PR["tce_txb_PR"]
        tc_api = nivels_api["tca_txb"] + nivels_api["tce_txb"]
        tc_pd = int((tc_pr + tc_api) / 2)

    elif modo_PR == "Taxicolectivo":
            
        tc_pr = nivels_PR["tca_txc_PR"] + nivels_PR["tce_txc_PR"]
        tc_api = nivels_api["tca_txb"] + nivels_api["tce_txb"] # La API no tiene tc para taxicolectivo, se usa el de taxibus
        tc_pd = int((tc_pr + tc_api) / 2)

    tc_pd_list = [tc_pd] * 8
    return tc_pd_list
    
def compute_te_pd_current_mode(modo_PR, nivels_PR):

    if modo_PR == "Auto Particular":

        te_pd = 0
        
    elif modo_PR == "Taxibus":

        te_pr = nivels_PR["te_txb_PR"]
        te_pd = min(max(3,int(te_pr)),10)

    elif modo_PR == "Taxicolectivo":
            
        te_pr = nivels_PR["te_txc_PR"]
        te_pd = min(max(3,int(te_pr)),10)

    te_pd_list = [te_pd] * 8
    return te_pd_list

### ------------------------------------------
### Funciones para calcular niveles de servicio PD
### Alternativa Hipotética (Tren, Tranvía, BRT)
### ------------------------------------------

def compute_c_pd_new_mode():
    columna_c_pd_list = [0,0,1,1,2,2,1,1]
    niveles_c_pd = {0: 1000, 1: 800, 2: 630}
    c_pd_list = [niveles_c_pd[c] for c in columna_c_pd_list]
    return c_pd_list

def compute_tc_pd_new_mode():
    origen = get_origin()
    destino = get_destination()

    isocrones_gdf = gpd.read_file("data/isocronas_troncal/isocronas_walk_troncal_antofa.shp")

    def identify_isochrone(punto):

        for time in range(4,33):
            isocrone_polygon = isocrones_gdf[isocrones_gdf["minutos"] == time].geometry.values[0]
            if isocrone_polygon.contains(gpd.points_from_xy([punto[1]], [punto[0]])[0]):
                return time
            
        return 32  # Si no está en ninguna isócrona, se asigna el valor máximo
    
    tc_origen = identify_isochrone(origen) 
    tc_destino = identify_isochrone(destino) 
    tc_total = tc_origen + tc_destino if tc_origen + tc_destino <= 10 else 10

    columna_tc_pd_list = [0,1,0,1,1,0,1,0]
    
    niveles_tc_pd = {0: tc_total - 4, 
                     1: tc_total}
    
    tc_pd_list = [niveles_tc_pd[tc] for tc in columna_tc_pd_list]
    return tc_pd_list


def compute_tv_pd_new_mode(modo_PR, tv1, tc1, tc2_mean, niveles_api):

    columna_tv_pd_list = [0,1,0,1,0,1,0,1]
    t1 = tv1 + tc1 if modo_PR != "Auto Particular" else tv1

    tv_liv_api = niveles_api["tv_liv"]
    tv_txb_api = niveles_api["tv_txb"]
    tc_txb_api = niveles_api["tca_txb"] + niveles_api["tce_txb"]

    t_liv_api = tv_liv_api
    t_txb_api = tv_txb_api + tc_txb_api

    ratio_api = t_txb_api / t_liv_api if t_txb_api > t_liv_api else 1.5

    if modo_PR == "Auto Particular" or modo_PR == "Taxicolectivo":
        ratio_mean = (1 + ratio_api) / 2
        f1 = (2 + 3 * ratio_mean ) / 5
        f2 = (4 * ratio_mean + 1 * ratio_api ) / 5
        
    elif modo_PR == "Taxibus":
        ratio_mean = (1 + 1/ratio_api) / 2
        f1 = (3 + 2 * ratio_mean ) / 5
        f2 = ratio_mean
 
    niveles_t_pd = {0: t1 * f1,
                    1: t1 * f2}

    t2_pd_list = [niveles_t_pd[tv] for tv in columna_tv_pd_list]

    tv_pd_list = [int(t2_pd_list[i] - tc2_mean) for i in range(len(t2_pd_list))]

    return tv_pd_list
    

def compute_te_pd_new_mode(te1):

    columna_te_pd_list = [0,1,1,0,0,1,1,0]

    if te1 <= 7:
        niveles_te_pd = {0: 4, 
                         1: 7}
    else:
        # Esta condición solo puede llega a ocurrir para modos PR Taxibus o Taxicolectivo
        niveles_te_pd = {0: te1 - 4, 
                         1: te1}
                
    te_pd_list = [niveles_te_pd[te] for te in columna_te_pd_list]
    return te_pd_list

### ------------------------------------------
### Función para generar diseño experimental PD
### ------------------------------------------

def generate_choice_set_df(nro_disenho):

    disenhos_df = pd.read_csv("data/disenhos_pd.csv", sep = ";")
    df = disenhos_df[disenhos_df["DIS"] == nro_disenho]
    df.set_index("Tj", inplace=True)

    return df

def apply_deltas_to_choice_set_df(modo_PR, df):

    df_modified = df.copy()

    delta_c = pd.Series([0,50,20,0]*2, index=df.index) 
    delta_tv = pd.Series([0,1,2]*2 + [0,1], index=df.index) 
    delta_tc = pd.Series([0,1]*4, index=df.index)
    delta_te = pd.Series([1,0]*4, index=df.index)

    delta_c = pd.Series([0]*8, index=df.index) 
    delta_tv = pd.Series([0]*8 , index=df.index) 
    delta_tc = pd.Series([0]*8, index=df.index)
    delta_te = pd.Series([0]*8, index=df.index)


    df_modified["c1"] = df_modified["c1"] + delta_c
    df_modified["tv1"] = df_modified["tv1"] + delta_tv
    df_modified["tc1"] = df_modified["tc1"] + delta_tc
    df_modified["te1"] = df_modified["te1"] + delta_te if modo_PR != "Auto Particular" else df_modified["te1"]

    df_modified["c2"] = df_modified["c2"] + delta_c
    df_modified["tv2"] = df_modified["tv2"] + delta_tv
    df_modified["tc2"] = df_modified["tc2"] + delta_tc
    df_modified["te2"] = df_modified["te2"] + delta_te if modo_PR != "Auto Particular" else df_modified["te2"]

    return df_modified

def compute_differences(df):
    df_diff = pd.DataFrame()
    df_diff['delta_c'] = df['c2'] - df['c1']
    df_diff['delta_tv'] = df['tv2'] - df['tv1']
    df_diff['delta_tc'] = df['tc2'] - df['tc1']
    df_diff['delta_te'] = df['te2'] - df['te1']
    return df_diff
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

def identify_mode(responses_dict):
    lugar = responses_dict["screen1"]["pc"]
    if lugar.startswith("Terminal"):
        return "Bus"
    else: 
        return "Auto Particular"

def identify_mode_2(responses_dict):
    lugar = responses_dict["screen1"]["pc"]
    if lugar.startswith("Terminal"):
        servicio_bus = responses_dict["screen52"]["asiento"]
        if servicio_bus == "Asiento Clásico o Semi-Cama":
            return "Bus"
        elif servicio_bus == "Salón Cama o Premium":
            return "Bus P"
    else: 
        return "Auto Particular"

def uniform_comuna(comuna):

    if comuna == "Licanray":
        return "Pucón"
    
    elif comuna == "Padre las casas":
        return "Temuco"
    
    else: 
        return comuna

def cargar_disenhos_df():
    disenhos_df = pd.read_csv("data/disenhos.csv", sep=";")
    disenhos_df.set_index("DIS", inplace=True)
    return disenhos_df

def get_id_disenho(disenhos_df, modo, origen, destino):
    filtro = ((disenhos_df["Origen"] == origen) &
              (disenhos_df["Destino"] == destino) &
              (disenhos_df["Modo"] == modo))
    disenhos_filtrados = disenhos_df[filtro]

    assert len(disenhos_filtrados) <= 1, "Error: Más de un diseño coincide con los criterios especificados."

    if len(disenhos_filtrados) == 0:
        return 0
    
    return disenhos_filtrados.index[0]

def identify_nro_disenho(disenhos_df, responses_dict):
    
    modo = identify_mode(responses_dict)
    origen = uniform_comuna(responses_dict["screen3"]["origen"])
    destino = uniform_comuna(responses_dict["screen3"]["destino"])

    id_disenho_od = get_id_disenho(disenhos_df, modo, origen, destino)
    id_disenho_do = get_id_disenho(disenhos_df, modo, destino, origen)

    id_disenho = id_disenho_od + id_disenho_do

    return id_disenho

def identify_nro_disenho_2(disenhos_df, responses_dict):
    
    modo = identify_mode_2(responses_dict)
    origen = uniform_comuna(responses_dict["screen3"]["origen"])
    destino = uniform_comuna(responses_dict["screen3"]["destino"])

    id_disenho_od = get_id_disenho(disenhos_df, modo, origen, destino)
    id_disenho_do = get_id_disenho(disenhos_df, modo, destino, origen)

    id_disenho = id_disenho_od + id_disenho_do

    return id_disenho

def validate_par_od(responses):

    df = cargar_disenhos_df()

    nro_disenho = identify_nro_disenho(df, responses)

    if nro_disenho == 0:
        st.session_state["od_screen_completed"] = True
        st.session_state["screen51_completed"] = True
        st.session_state["screen52_completed"] = True
        st.session_state["screen53_completed"] = True
        st.session_state["screen6_completed"] = True
        st.session_state["order_pd_choice_sets"] = []
        st.session_state["screen15_completed"] = True

        return False
    
    return True


def get_default_current_mode(id_disenho, disenhos_df):
    row = disenhos_df.loc[id_disenho]

    df_dict = {
        "label1": [row["Modo"].split()[0]] * 8,
        "c1": [row["c_ref"]] * 8,
        "tv1": [row["tv_ref"]] * 8,
        "ta1": [row["ta_ref"]] * 8,
        "f1": [row["f_ref"]] * 8
    }

    df = pd.DataFrame(df_dict, index=range(1,9))

    return df

def generate_definitive_level(default_level, pr_level, percentage, multiple):

    upper_bound = get_nearest_multiple(default_level * (1 + percentage / 100), multiple)
    lower_bound = get_nearest_multiple(default_level * (1 - percentage / 100), multiple)

    if pr_level >= lower_bound and pr_level <= upper_bound:
        definitive_level = pr_level

    elif pr_level < lower_bound:
        definitive_level = default_level

    elif pr_level > upper_bound:
        definitive_level = upper_bound

    return definitive_level

def generate_current_mode_df(default_current_mode_df):

    current_mode_df = default_current_mode_df.copy()

    pr_nivels = get_nivels_PR()

    modo = default_current_mode_df.loc[1, "label1"]

    c_default = default_current_mode_df.loc[1, "c1"]
    tv_default = default_current_mode_df.loc[1, "tv1"]
    ta_default = default_current_mode_df.loc[1, "ta1"]

    if modo == "Auto":
        c_pr = get_nearest_multiple(pr_nivels["cb_liv_PR"] + pr_nivels["cp_liv_PR"], 500)
        tv_pr = get_nearest_multiple(pr_nivels["tv_liv_PR"], 5)
        ta_pr = 0
        current_mode_df["f1"] = "No Aplica"

    elif modo == "Bus":
        c_pr = get_nearest_multiple(pr_nivels["c_bus_PR"], 500)
        tv_pr = get_nearest_multiple(pr_nivels["tv_bus_PR"], 5)
        ta_pr = get_nearest_multiple(pr_nivels["ta_bus_PR"] + pr_nivels["te_bus_PR"], 5)
        current_mode_df["f1"] = "Cada 15 minutos"

    c = generate_definitive_level(c_default, c_pr, 30, 500)
    tv = generate_definitive_level(tv_default, tv_pr, 20, 5)
    ta = generate_definitive_level(ta_default, ta_pr, 35, 5)

    
    current_mode_df["c1"] = c
    current_mode_df["tv1"] = tv
    current_mode_df["ta1"] = ta

    return current_mode_df

def generate_orthogonal_design_df():

    df_dict = {
        "tv": [0,1,0,1,0,1,0,1],
        "c": [0,0,1,1,2,2,1,1],
        "f": [0,1,0,1,1,0,1,0],
        "ta": [0,1,1,0,0,1,1,0]
    }

    df = pd.DataFrame(df_dict, index=range(1,9))

    return df

def get_diferences_levels(id_disenho, disenhos_df):
    row = disenhos_df.loc[id_disenho]

    c_dict = {0: row["c_0"],
              1: row["c_1"],
              2: row["c_2"]}
    
    tv_dict = {0: row["tv_0"],
               1: row["tv_1"]}
    
    ta_dict = {0: row["ta_0"],
               1: row["ta_1"]}
    
    f_dict = {0: row["f_0"],
              1: row["f_1"]}
    
    orthogonal_design_df = generate_orthogonal_design_df()
    differences_df = orthogonal_design_df.copy()
    
    differences_df['c'] = orthogonal_design_df['c'].map(c_dict)
    differences_df['tv'] = orthogonal_design_df['tv'].map(tv_dict)
    differences_df['ta'] = orthogonal_design_df['ta'].map(ta_dict)
    differences_df['f'] = orthogonal_design_df['f'].map(f_dict)

    return differences_df

def generate_new_mode_df(current_mode_df, differences_df):
    new_mode_df = pd.DataFrame(index=current_mode_df.index)

    new_mode_df['label2'] = "Tren"
    new_mode_df['c2'] = current_mode_df['c1'] + differences_df['c']
    new_mode_df['tv2'] = current_mode_df['tv1'] + differences_df['tv']
    new_mode_df['ta2'] = current_mode_df['ta1'] + differences_df['ta']
    new_mode_df['f2'] = differences_df['f'].astype(str) + " al día"

    return new_mode_df

def generate_dis_column_df(id_disenho):
    dis_column_df = pd.DataFrame({'DIS': [id_disenho]*8}, index=range(1,9))
    return dis_column_df

### ------------------------------------------
### Función para generar diseño experimental PD
### ------------------------------------------

def generate_choice_set_df(responses):

    df = cargar_disenhos_df()

    nro_disenho = identify_nro_disenho_2(df, responses)

    dis_column_df = generate_dis_column_df(nro_disenho)
    default_current_mode_df = get_default_current_mode(nro_disenho, df)
    current_mode_df = generate_current_mode_df(default_current_mode_df)
    differences_df = get_diferences_levels(nro_disenho, df)
    new_mode_df = generate_new_mode_df(current_mode_df, differences_df)

    df = pd.concat([dis_column_df, current_mode_df, new_mode_df], axis=1)
    
    df_modified = apply_deltas_to_choice_set_df(df)

    return df_modified

def apply_deltas_to_choice_set_df(df):

    df_modified = df.copy()

    delta_c = pd.Series([0,1000,500,-500]*2, index=df.index) 
    delta_tv = pd.Series([0,5,-5,5,-5,0,5,0], index=df.index) 

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
import streamlit as st

from src.time_utils import process_time_list, record_datetime
from src.database import send_to_database
from src.pd_utils import generate_choice_set_df, compute_differences
from src.api_nivels import save_api_nivels
import random

import ui.general_screen as gs
import ui.od_screen as od
import ui.pd_screen as pds
import ui.restart_screen as rs

# --------------------------------------------------
# Configuración general de la app
# --------------------------------------------------
st.set_page_config(
    page_title = "PD",
    layout="centered",
    initial_sidebar_state="auto"
)

# --------------------------------------------------
# Variables de Estado
# --------------------------------------------------

# Variables de estado para controlar la navegación entre pantallas

# Screen1: Encuestador y Lugar de Encuesta
if "screen1_completed" not in st.session_state:
    st.session_state["screen1_completed"] = False

# Screen2: Características del Usuario
if "screen2_completed" not in st.session_state:
    st.session_state["screen2_completed"] = False

# Screen3: Características del Viaje
if "screen3_completed" not in st.session_state:
    st.session_state["screen3_completed"] = False

# OD Screen: Origen y Destino del Viaje
if "od_screen_completed" not in st.session_state:
    st.session_state["od_screen_completed"] = False

# Screen51: Niveles Servicio PR Automóvil
if "screen51_completed" not in st.session_state:
    st.session_state["screen51_completed"] = False

# Screen52: Niveles Servicio PR Taxibus
if "screen52_completed" not in st.session_state:
    st.session_state["screen52_completed"] = False
    
# Screen53: Niveles Servicio PR Taxicolectivos
if "screen53_completed" not in st.session_state:
    st.session_state["screen53_completed"] = False

# Screen 6: Introducción Preferencias Declaradas
if "screen6_completed" not in st.session_state:
    st.session_state["screen6_completed"] = False

# Order PD Choice Sets: Orden Tarjetas PD
if "order_pd_choice_sets" not in st.session_state:
    st.session_state["order_pd_choice_sets"] = random.sample(range(1, 9), 8)

# Screen5: Categoría de Usuario
if "screen15_completed" not in st.session_state:
    st.session_state["screen15_completed"] = False

# Variable para almacenar las respuestas

if "responses" not in st.session_state:
    st.session_state["responses"] = {}

# Variable para almacenar la hora de inicio en cada pantalla

if "time_list" not in st.session_state:
    st.session_state["time_list"] = []

if "responses_sent" not in st.session_state:
    st.session_state["responses_sent"] = False

# --------------------------------------------------
# Screen 1 // General Screen // Encuestador y Lugar de Encuesta
# --------------------------------------------------

if not st.session_state["screen1_completed"]:

    gs.generate_general_screen(id_screen=1)

# --------------------------------------------------
# Screen 2 // General Screen // Características del Usuario
# --------------------------------------------------

if st.session_state["screen1_completed"] and not st.session_state["screen2_completed"]:

    record_datetime()

    gs.generate_general_screen(id_screen=2)

# --------------------------------------------------
# Screen 3 // General Screen // Características del Viaje
# --------------------------------------------------

if st.session_state["screen2_completed"] and not st.session_state["screen3_completed"]:

    gs.generate_general_screen(id_screen=3)

# --------------------------------------------------
# Screen 4 // OD Screen // Origen y Destino del Viaje
# --------------------------------------------------

if st.session_state["screen3_completed"] and not st.session_state["od_screen_completed"]:

    od.generate_od_screen()

# --------------------------------------------------
# Screen 5x // Conditional General Screen // Niveles de Servicio Modo PR
# --------------------------------------------------

screen_5x_completed = any([
    st.session_state["screen51_completed"],
    st.session_state["screen52_completed"],
    st.session_state["screen53_completed"]
])

if st.session_state["od_screen_completed"] and not screen_5x_completed:

    #save_api_nivels() # Se consultan y guardan los niveles de servicio vía API Directions de Google

    modo_PR = st.session_state["responses"]["screen3"].get("modo_PR", False)

    if modo_PR == "Auto Particular":
        gs.generate_general_screen(id_screen=51)

    elif modo_PR == "Bus":
        gs.generate_general_screen(id_screen=52)


# --------------------------------------------------
# Screen 6 // General Screen // Introdución Preferencias Declaradas
# --------------------------------------------------

if screen_5x_completed and not st.session_state["screen6_completed"]:

    gs.generate_general_screen(id_screen=6)

# --------------------------------------------------
# Screen 7 .. 14 // PD Screen // Perfiles de Elección PDs
# --------------------------------------------------

if st.session_state["screen6_completed"] and len(st.session_state["order_pd_choice_sets"]) > 0:
    
    pds.initialize_pd_responses()

    if "choice_set_df" not in st.session_state:
        st.session_state["choice_set_df"] = generate_choice_set_df(nro_disenho=1)
        #st.session_state["choice_set_df_differences"] = compute_differences(st.session_state["choice_set_df"])

    pds.generate_pd_screen(st.session_state["order_pd_choice_sets"][0])

# --------------------------------------------------
# Screen 15 // General Screen // Categoría de Usuario
# --------------------------------------------------

if len(st.session_state["order_pd_choice_sets"]) == 0 and not st.session_state["screen15_completed"]:

    gs.generate_general_screen(id_screen=15)

# --------------------------------------------------
# Screen 16 // Restart Screen // Nueva Encuesta
# --------------------------------------------------

if st.session_state["screen15_completed"]:

    process_time_list()

    #Enviar Respuestas a BBDD online
    #if not st.session_state["responses_sent"]:
    #    send_to_database(st.session_state["responses"])

    rs.generate_restart_screen()


st.divider()

st.write(st.session_state["responses"])




if "choice_set_df" in st.session_state:
        st.write(st.session_state["choice_set_df"])
        st.write(st.session_state["choice_set_df_differences"])
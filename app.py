import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from streamlit_option_menu import option_menu

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
# ==========================================
st.set_page_config(page_title="IdeaLab M3 | UCV", page_icon="💡", layout="wide")

# Inyectamos CSS para mejorar la estética y los botones
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main-title {
        font-size: 3.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding: 0.5rem 0; margin-bottom: 0;
    }
    .subtitle {
        text-align: center; color: #4facfe; font-size: 1.2rem; 
        margin-bottom: 2rem; letter-spacing: 2px; text-transform: uppercase;
    }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 1.8rem; margin-bottom: 1.2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border: none; color: #050505 !important; font-weight: 800;
        border-radius: 14px; padding: 0.7rem 1.5rem; transition: 0.4s;
    }
    /* Estilo especial para botón de retorno */
    .btn-return>button {
        background: transparent !important;
        border: 1px solid #4facfe !important;
        color: #4facfe !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN A FIREBASE (CON SEGURIDAD)
# ==========================================
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        try:
            if "firebase" in st.secrets:
                creds = dict(st.secrets["firebase"])
                cred = credentials.Certificate(creds)
            else:
                cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error Crítico de Conexión: {e}")
            return None
    return firestore.client()

db = get_db()

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN Y SESIÓN
# ==========================================
if 'menu_option' not in st.session_state:
    st.session_state['menu_option'] = "IdeaLabM3"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Función para forzar el regreso al inicio
def go_home():
    st.session_state['menu_option'] = "IdeaLabM3"
    st.rerun()

# ==========================================
# 4. SIDEBAR Y MENÚ
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # El menú ahora se sincroniza con el session_state
    selected = option_menu(
        menu_title="Navegación", 
        options=["IdeaLabM3", "Estudiantes", "Mentores", "Administrador"],
        icons=["rocket-takeoff", "mortarboard", "person-badge", "speedometer2"], 
        menu_icon="cast", 
        default_index=0,
        key="main_menu"
    )
    # Actualizamos la opción elegida
    st.session_state['menu_option'] = selected

    if st.session_state['authenticated']:
        st.divider()
        st.caption(f"Usuario: {st.session_state.get('mentor_name', 'Admin')}")
        if st.button("Cerrar Sesión"):
            st.session_state['authenticated'] = False
            st.rerun()

# ==========================================
# 5. RENDERIZADO DE SECCIONES
# ==========================================
current_menu = st.session_state['menu_option']

if current_menu == "IdeaLabM3":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Donde las ideas convergen</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="card" style="text-align: center;">
            <h2 style="color:#00f2fe;">¡Bienvenido al Hub de Innovación de la UCV! 🚀</h2>
            <p>Selecciona una opción en el menú lateral para comenzar tu viaje de emprendimiento.</p>
        </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif current_menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Estudiantes</h1>', unsafe_allow_html=True)
    
    # BOTÓN DE RETORNO AL INICIO
    if st.button("⬅️ Volver a IdeaLabM3", key="ret_est"):
        go_home()

    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    # ... (Resto del código de registro y consultas igual que antes)
    with t1:
        st.info("Regístrate para comenzar tus mentorías.")
        # Lógica de formulario...
        
elif current_menu == "Mentores":
    st.markdown('<h1 class="main-title">Panel de Mentores</h1>', unsafe_allow_html=True)
    
    # BOTÓN DE RETORNO AL INICIO
    if st.button("⬅️ Volver a IdeaLabM3", key="ret_men"):
        go_home()

    if not st.session_state['authenticated']:
        # Lógica de Login...
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar"):
                # Aquí llamarías a tu función check_login de antes
                pass
    else:
        st.success("Bandeja de entrada de mentorías activa.")

elif current_menu == "Administrador":
    st.markdown('<h1 class="main-title">Dashboard Admin</h1>', unsafe_allow_html=True)
    
    if st.button("⬅️ Volver a IdeaLabM3", key="ret_admin"):
        go_home()
        
    # Lógica de gráficos de Plotly...

st.sidebar.markdown("---")
st.sidebar.caption("IdealabM3 v5.8 | @UCV 2026")

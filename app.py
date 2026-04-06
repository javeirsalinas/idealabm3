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
        border-radius: 14px; padding: 0.7rem 1.5rem; transition: 0.4s; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN A FIREBASE
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
            st.error(f"Error de Conexión: {e}")
            return None
    return firestore.client()

db = get_db()

# Listas de Selección UCV
CAMPUS_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Arquitectura", "Medicina Humana", "Ciencias de la Comunicación", "Educación"]

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    
    menu = option_menu(
        menu_title="Menú Principal", 
        options=["IdeaLabM3", "Estudiantes", "Mentores", "Administrador"],
        icons=["rocket-takeoff", "mortarboard", "person-badge", "speedometer2"], 
        menu_icon="cast", default_index=0
    )

# ==========================================
# 4. SECCIÓN: IDEALABM3 (INICIO)
# ==========================================
if menu == "IdeaLabM3":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Donde las ideas convergen</p>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

# ==========================================
# 5. SECCIÓN: ESTUDIANTES (REGISTRO COMPLETO)
# ==========================================
elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Panel Estudiantil</h1>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with t1:
        st.markdown('<div class="card"><h3>Registro de Nuevo Estudiante</h3>', unsafe_allow_html=True)
        with st.form("registro_estudiante", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre Completo")
                correo = st.text_input("Correo Institucional (@ucvvirtual.edu.pe)")
                password = st.text_input("Crea una Contraseña", type="password")
            with col2:
                campus = st.selectbox("Campus UCV", CAMPUS_UCV)
                carrera = st.selectbox("Carrera Profesional", CARRERAS_UCV)
            
            submit = st.form_submit_button("Finalizar Registro 🚀")
            
            if submit:
                if nombre and correo and password:
                    try:
                        # Guardar en la colección 'students'
                        db.collection("students").document(correo).set({
                            "name": nombre,
                            "email": correo,
                            "password": password, # Se guarda para futuras validaciones
                            "campus": campus,
                            "career": carrera,
                            "createdAt": datetime.now()
                        })
                        st.success(f"¡Bienvenido {nombre}! Tu perfil en el campus {campus} ha sido creado.")
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.warning("Por favor, completa todos los campos obligatorios.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="card"><h3>Enviar Consulta al Mentor</h3>', unsafe_allow_html=True)
        correo_val = st.text_input("Confirma tu correo para enviar")
        consulta = st.text_area("Describe tu idea o problema de Misión 3")
        if st.button("Enviar Consulta"):
            if correo_val and consulta:
                # Verificar si el estudiante existe para traer su campus automáticamente
                student_ref = db.collection("students").document(correo_val).get()
                if student_ref.exists:
                    campus_auto = student_ref.to_dict().get('campus', 'No especificado')
                    db.collection("queries").add({
                        "student_email": correo_val,
                        "campus": campus_auto,
                        "text": consulta,
                        "status": "pending",
                        "createdAt": datetime.now()
                    })
                    st.success("¡Consulta enviada! Los mentores te responderán pronto.")
                else:
                    st.error("Correo no encontrado. Regístrate primero en la pestaña anterior.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        st.markdown('<h3>Tus Consultas</h3>', unsafe_allow_html=True)
        ver_correo = st.text_input("Ingresa tu correo para ver respuestas", key="ver_res")
        if ver_correo:
            consultas = db.collection("queries").where("student_email", "==", ver_correo).get()
            if consultas:
                for doc in consultas:
                    q = doc.to_dict()
                    with st.expander(f"Consulta del {q['createdAt'].strftime('%d/%m/%Y')}"):
                        st.write(f"**Tu pregunta:** {q['text']}")
                        if 'mentor_reply' in q:
                            st.info(f"**Respuesta del Mentor:** {q['mentor_reply']}")
                        else:
                            st.warning("Estado: Pendiente de respuesta.")
            else:
                st.info("No tienes consultas registradas con este correo.")

# El resto de secciones (Mentores/Admin) siguen la misma lógica estandarizada.
elif menu == "Mentores":
    st.markdown('<h1 class="main-title">Mentores</h1>', unsafe_allow_html=True)
    st.info("Inicia sesión para revisar las consultas pendientes de tus estudiantes.")
    # (Aquí va tu lógica de login de mentores que ya configuramos)

elif menu == "Administrador":
    st.markdown('<h1 class="main-title">Dashboard</h1>', unsafe_allow_html=True)
    # (Aquí va tu lógica de gráficos de Plotly)

st.sidebar.markdown("---")
st.sidebar.caption("IdealabM3 v5.9 | @UCV 2026")

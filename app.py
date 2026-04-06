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

# Listas UCV
CAMPUS_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Arquitectura", "Medicina Humana", "Ciencias de la Comunicación", "Educación"]

# ==========================================
# 3. LÓGICA DE SESIÓN (LOGIN)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_login(email, password):
    try:
        mentor_ref = db.collection("authorized_mentors").document(email).get()
        if mentor_ref.exists:
            data = mentor_ref.to_dict()
            if str(data.get('password')) == str(password):
                st.session_state['authenticated'] = True
                st.session_state['mentor_name'] = data.get('name', 'Mentor')
                return True
    except Exception as e:
        st.error(f"Error en la validación: {e}")
    return False

# ==========================================
# 4. NAVEGACIÓN
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
    if st.session_state['authenticated']:
        st.success(f"Conectado: {st.session_state['mentor_name']}")
        if st.button("Cerrar Sesión"):
            st.session_state['authenticated'] = False
            st.rerun()

# ==========================================
# 5. SECCIONES
# ==========================================
if menu == "IdeaLabM3":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Donde las ideas convergen</p>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Estudiantes</h1>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    with t1:
        with st.form("reg"):
            c1, c2 = st.columns(2)
            with c1: 
                n = st.text_input("Nombre Completo")
                e = st.text_input("Correo Institucional")
                p = st.text_input("Crea una contraseña", type="password")
            with c2:
                s = st.selectbox("Campus UCV", CAMPUS_UCV)
                ca = st.selectbox("Carrera Profesional", CARRERAS_UCV)
            if st.form_submit_button("Finalizar Registro 🚀"):
                db.collection("students").document(e).set({"name":n, "email":e, "password":p, "campus":s, "career":ca, "createdAt":datetime.now()})
                st.success("¡Perfil Creado!")
    # (T2 y T3 igual que v5.9)

elif menu == "Mentores":
    st.markdown('<h1 class="main-title">Panel de Mentores</h1>', unsafe_allow_html=True)
    
    if not st.session_state['authenticated']:
        st.markdown('<div class="card"><h3>Acceso Restringido</h3>', unsafe_allow_html=True)
        with st.form("login_mentores"):
            u_mail = st.text_input("Correo Institucional Autorizado")
            u_pass = st.text_input("Contraseña de Acceso", type="password")
            if st.form_submit_button("Ingresar al Panel"):
                if check_login(u_mail, u_pass):
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario no autorizado.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Bandeja de consultas para mentores
        docs = db.collection("queries").where("status", "==", "pending").get()
        if not docs:
            st.info("No hay consultas pendientes por el momento. 🎉")
        for doc in docs:
            q = doc.to_dict()
            with st.container():
                st.markdown(f'<div class="card"><h4>De: {q.get("student_email")}</h4><p><b>Campus:</b> {q.get("campus")}</p><p>{q["text"]}</p></div>', unsafe_allow_html=True)
                with st.expander("Responder esta consulta"):
                    ans = st.text_area("Escribe tu asesoría aquí:", key=doc.id)
                    if st.button("Enviar Respuesta 📩", key=f"b_{doc.id}"):
                        db.collection("queries").document(doc.id).update({
                            "status": "responded",
                            "mentor_reply": ans,
                            "repliedAt": datetime.now()
                        })
                        st.success("Respuesta enviada correctamente.")
                        st.rerun()

elif menu == "Administrador":
    if not st.session_state['authenticated']:
        st.warning("🔒 Debes iniciar sesión en la pestaña 'Mentores' para ver las estadísticas.")
    else:
        st.markdown('<h1 class="main-title">Administrador</h1>', unsafe_allow_html=True)
        q_docs = db.collection("queries").get()
        s_docs = db.collection("students").get()
        if q_docs:
            df = pd.DataFrame([d.to_dict() for d in q_docs])
            c1, c2, c3 = st.columns(3)
            c1.metric("Consultas Totales", len(df))
            c2.metric("Alumnos Registrados", len(s_docs))
            c3.metric("Casos Resueltos", len(df[df['status'] == 'responded']) if 'status' in df.columns else 0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if 'campus' in df.columns:
                    fig = px.bar(df, x="campus", title="Consultas por Campus", template="plotly_dark", color="campus")
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                if 'status' in df.columns:
                    fig_pie = px.pie(df, names="status", title="Estado de Atención", hole=0.4, template="plotly_dark")
                    st.plotly_chart(fig_pie, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdealabM3 v6.0 | @UCV 2026")

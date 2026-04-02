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
        padding: 1rem 0; margin-bottom: 1rem;
    }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 1.8rem; margin-bottom: 1.2rem;
    }
    .badge {
        display: inline-block; padding: 5px 15px; border-radius: 50px;
        font-size: 0.75rem; font-weight: 700; background: rgba(79, 172, 254, 0.15);
        color: #4facfe; text-transform: uppercase; margin-bottom: 12px;
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

# ==========================================
# 3. LÓGICA DE AUTENTICACIÓN SIMPLE
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_login(email, password):
    # Aquí consultamos la colección de mentores autorizados
    mentor_ref = db.collection("authorized_mentors").document(email).get()
    if mentor_ref.exists:
        data = mentor_ref.to_dict()
        if data['password'] == password:
            st.session_state['authenticated'] = True
            st.session_state['mentor_name'] = data.get('name', 'Mentor')
            return True
    return False

# ==========================================
# 4. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    
    options = ["IdealabM3", "Estudiantes", "Mentores", "Administrador"]
    icons = ["rocket-takeoff", "mortarboard", "person-badge", "speedometer2"]
    
    menu = option_menu(
        menu_title="Misión 3 Menú", options=options, icons=icons, 
        menu_icon="cast", default_index=0,
        styles={
            "container": {"background-color": "#0a0a0a"},
            "nav-link-selected": {"background-color": "#4facfe", "color": "#050505"},
        }
    )
    
    if st.session_state['authenticated']:
        st.success(f"Sesión: {st.session_state['mentor_name']}")
        if st.button("Cerrar Sesión"):
            st.session_state['authenticated'] = False
            st.rerun()

# Listas UCV
SEDES_UCV = ["Lima Norte", "Ate", "SJL", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Ingeniería Civil", "Arquitectura", "Medicina Humana", "Enfermería", "Arte y Diseño Gráfico Empresarial"]

# ==========================================
# 5. CONTENIDO POR SECCIÓN
# ==========================================
st.markdown(f'<h1 class="main-title">{menu}</h1>', unsafe_allow_html=True)

if menu == "IdealabM3":
    st.markdown('<div class="card"><h2>Innovación Vallejiana 🚀</h2><p>Bienvenido al ecosistema IdealabM3.</p></div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    with t1:
        with st.form("reg"):
            n = st.text_input("Nombre")
            e = st.text_input("Correo")
            s = st.selectbox("Sede", SEDES_UCV)
            c = st.selectbox("Carrera", CARRERAS_UCV)
            if st.form_submit_button("Registrarse"):
                db.collection("students").document(e).set({"name":n, "email":e, "campus":s, "career":c, "createdAt":datetime.now()})
                st.success("¡Perfil Creado!")
    with t2:
        ev = st.text_input("Tu Correo")
        tq = st.text_area("Consulta")
        if st.button("Enviar"):
            db.collection("queries").add({"student_email":ev, "text":tq, "category":"General", "status":"pending", "createdAt":datetime.now()})
            st.toast("Enviado 🚀")
    with t3:
        ck = st.text_input("Ingresa tu correo para ver respuestas")
        if ck:
            res = db.collection("queries").where("student_email", "==", ck).get()
            for d in res:
                q = d.to_dict()
                st.markdown(f'<div class="card"><b>Consulta:</b> {q["text"]}</div>', unsafe_allow_html=True)
                if q.get("mentor_reply"): st.info(f"Respuesta: {q['mentor_reply']}")

elif menu in ["Mentores", "Administrador"]:
    if not st.session_state['authenticated']:
        st.warning("🔒 Esta sección es exclusiva para Mentores y Administradores.")
        with st.form("login_form"):
            user_mail = st.text_input("Correo de Mentor")
            user_pass = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar"):
                if check_login(user_mail, user_pass):
                    st.success("Acceso concedido")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o no autorizado.")
    else:
        # CONTENIDO PARA MENTORES
        if menu == "Mentores":
            docs = db.collection("queries").where("status", "==", "pending").get()
            if not docs: st.info("No hay consultas pendientes.")
            for doc in docs:
                q = doc.to_dict()
                with st.container():
                    st.markdown(f'<div class="card"><h3>De: {q.get("student_email")}</h3><p>{q["text"]}</p></div>', unsafe_allow_html=True)
                    with st.expander("Responder"):
                        ans = st.text_area("Asesoría:", key=doc.id)
                        if st.button("Enviar", key=f"b_{doc.id}"):
                            db.collection("queries").document(doc.id).update({"status":"responded", "mentor_reply":ans, "repliedAt":datetime.now()})
                            st.rerun()
        
        # CONTENIDO PARA ADMINISTRADOR
        elif menu == "Administrador":
            q_docs = db.collection("queries").get()
            s_docs = db.collection("students").get()
            if q_docs:
                df = pd.DataFrame([d.to_dict() for d in q_docs])
                c1, c2, c3 = st.columns(3)
                c1.metric("Consultas", len(df))
                c2.metric("Estudiantes", len(s_docs))
                c3.metric("Resueltas", len(df[df['status'] == 'responded']))
                st.plotly_chart(px.pie(df, names="category", hole=0.5, template="plotly_dark"), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdealabM3 v5.0 | @UCV 2026")

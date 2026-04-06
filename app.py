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

CAMPUS_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Arquitectura", "Medicina Humana", "Ciencias de la Comunicación", "Educación"]

# ==========================================
# 3. LÓGICA DE SESIÓN
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
        st.error(f"Error: {e}")
    return False

# ==========================================
# 4. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    menu = option_menu(
        menu_title="Menú Principal", 
        options=["IdeaLabM3", "Estudiantes", "Mentores", "Administrador"],
        icons=["rocket-takeoff", "mortarboard", "person-badge", "speedometer2"], 
        menu_icon="cast", default_index=0
    )
    if st.session_state['authenticated']:
        st.info(f"Conectado: {st.session_state['mentor_name']}")
        if st.button("Cerrar Sesión"):
            st.session_state['authenticated'] = False
            st.rerun()

# ==========================================
# 5. CONTENIDO POR SECCIONES
# ==========================================

if menu == "IdeaLabM3":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Donde las ideas convergen</p>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Estudiantes</h1>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with t1:
        st.markdown('<div class="card"><h3>Registro de Perfil</h3>', unsafe_allow_html=True)
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Nombre Completo")
                e = st.text_input("Correo Institucional")
                p = st.text_input("Crea una contraseña", type="password")
            with c2:
                s = st.selectbox("Campus UCV", CAMPUS_UCV)
                ca = st.selectbox("Carrera Profesional", CARRERAS_UCV)
            if st.form_submit_button("Finalizar Registro"):
                if n and e and p:
                    db.collection("students").document(e).set({"name":n, "email":e, "password":p, "campus":s, "career":ca, "createdAt":datetime.now()})
                    st.success("¡Perfil creado con éxito!")
                else: st.warning("Completa todos los campos.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="card"><h3>Enviar Consulta</h3>', unsafe_allow_html=True)
        with st.form("consulta_form", clear_on_submit=True):
            correo_consulta = st.text_input("Confirma tu correo")
            texto_consulta = st.text_area("Escribe tu duda técnica")
            if st.form_submit_button("Enviar 📩"):
                if correo_consulta and texto_consulta:
                    student_doc = db.collection("students").document(correo_consulta).get()
                    if student_doc.exists:
                        campus_val = student_doc.to_dict().get('campus', 'No especificado')
                        db.collection("queries").add({"student_email": correo_consulta, "campus": campus_val, "text": texto_consulta, "status": "pending", "createdAt": datetime.now()})
                        st.success("Consulta enviada.")
                    else: st.error("Correo no registrado.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        ver_correo = st.text_input("Correo para ver respuestas")
        if ver_correo:
            docs = db.collection("queries").where("student_email", "==", ver_correo).get()
            for doc in docs:
                data = doc.to_dict()
                with st.expander(f"Consulta: {data['text'][:30]}..."):
                    st.write(data['text'])
                    if 'mentor_reply' in data: st.info(f"Respuesta: {data['mentor_reply']}")

elif menu == "Mentores":
    st.markdown('<h1 class="main-title">Mentores</h1>', unsafe_allow_html=True)
    if not st.session_state['authenticated']:
        with st.form("login_m"):
            u = st.text_input("Correo Mentor")
            p = st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar"):
                if check_login(u, p): st.rerun()
                else: st.error("Datos incorrectos.")
    else:
        docs = db.collection("queries").where("status", "==", "pending").get()
        for doc in docs:
            q = doc.to_dict()
            with st.container():
                st.markdown(f'<div class="card"><h4>De: {q.get("student_email")}</h4><p>{q["text"]}</p></div>', unsafe_allow_html=True)
                ans = st.text_area("Responder:", key=doc.id)
                if st.button("Enviar", key=f"b_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status": "responded", "mentor_reply": ans, "repliedAt": datetime.now()})
                    st.rerun()

elif menu == "Administrador":
    if not st.session_state['authenticated']:
        st.warning("Inicia sesión en Mentores primero.")
    else:
        st.markdown('<h1 class="main-title">Dashboard</h1>', unsafe_allow_html=True)
        q_docs = db.collection("queries").get()
        if q_docs:
            df = pd.DataFrame([d.to_dict() for d in q_docs])
            fig = px.bar(df, x="campus", title="Consultas por Campus", template="plotly_dark", color="campus")
            st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdealabM3 v6.1 | @UCV 2026")

import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
from streamlit_option_menu import option_menu
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. CONFIGURACIÓN Y ESTILO
# ==========================================
st.set_page_config(page_title="IdeaLab M3 | UCV", page_icon="💡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main-title {
        font-size: 3rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
    }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN FIREBASE
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
            st.error(f"Error Firebase: {e}")
            return None
    return firestore.client()

db = get_db()

CAMPUS_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Arquitectura", "Medicina Humana", "Ciencias de la Comunicación", "Educación"]

# ==========================================
# 3. LÓGICA DE SESIÓN (ESTUDIANTES Y MENTORES)
# ==========================================
if 'auth_user' not in st.session_state:
    st.session_state['auth_user'] = None  # Para Estudiantes
if 'auth_mentor' not in st.session_state:
    st.session_state['auth_mentor'] = False # Para Mentores

# ==========================================
# 4. FUNCIÓN DE EMAIL
# ==========================================
def enviar_notificacion(destinatario, respuesta, duda_original):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASS"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "💡 IdeaLabM3: Respuesta a tu consulta"
        cuerpo = f"<html><body><div style='padding:20px;background:#f0f2f6;'><h3>Hola!</h3><p>Tu consulta: {duda_original}</p><p><b>Respuesta:</b> {respuesta}</p></div></body></html>"
        msg.attach(MIMEText(cuerpo, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
    except: pass

# ==========================================
# 5. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    menu = option_menu("IdeaLabM3", ["Inicio", "Estudiantes", "Mentores", "Administrador"], 
                       icons=['house', 'mortarboard', 'person-check', 'graph-up'], default_index=0)
    
    if st.session_state['auth_user'] or st.session_state['auth_mentor']:
        if st.button("Cerrar Sesión Global"):
            st.session_state['auth_user'] = None
            st.session_state['auth_mentor'] = False
            st.rerun()

# ==========================================
# 6. SECCIONES
# ==========================================

if menu == "Inicio":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Donde las ideas convergen</p>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Panel Estudiantil</h1>', unsafe_allow_html=True)
    
    if st.session_state['auth_user'] is None:
        tab_log, tab_reg = st.tabs(["🔑 Ingresar", "📝 Registrarse"])
        
        with tab_log:
            with st.form("login_estudiante"):
                log_email = st.text_input("Correo Institucional")
                log_pass = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar"):
                    u_ref = db.collection("students").document(log_email).get()
                    if u_ref.exists and str(u_ref.to_dict().get('password')) == log_pass:
                        st.session_state['auth_user'] = u_ref.to_dict()
                        st.rerun()
                    else: st.error("Correo o clave incorrectos")
        
        with tab_reg:
            with st.form("reg_estudiante"):
                n, e, p = st.text_input("Nombre Completo"), st.text_input("Correo"), st.text_input("Crea Clave", type="password")
                s, ca = st.selectbox("Sede", CAMPUS_UCV), st.selectbox("Carrera", CARRERAS_UCV)
                if st.form_submit_button("Registrarme"):
                    db.collection("students").document(e).set({"name":n, "email":e, "password":p, "campus":s, "career":ca})
                    st.success("¡Registrado! Ahora ingresa por la pestaña de 'Ingresar'.")
    else:
        # USUARIO YA LOGUEADO
        st.info(f"Bienvenido/a, {st.session_state['auth_user']['name']}")
        t_con, t_res = st.tabs(["🚀 Nueva Consulta", "📩 Mis Respuestas"])
        
        with t_con:
            with st.form("consulta_f", clear_on_submit=True):
                duda = st.text_area("¿En qué podemos ayudarte hoy?")
                if st.form_submit_button("Enviar a Mentores"):
                    db.collection("queries").add({
                        "student_email": st.session_state['auth_user']['email'],
                        "campus": st.session_state['auth_user']['campus'],
                        "career": st.session_state['auth_user']['career'],
                        "text": duda, "status": "pending", "createdAt": datetime.now()
                    })
                    st.success("Consulta enviada correctamente.")
        
        with t_res:
            qs = db.collection("queries").where(filter=FieldFilter("student_email", "==", st.session_state['auth_user']['email'])).get()
            for doc in qs:
                q = doc.to_dict()
                with st.expander(f"Consulta: {q['text'][:30]}..."):
                    st.write(q['text'])
                    if 'mentor_reply' in q: st.info(f"Respuesta del Mentor: {q['mentor_reply']}")
                    else: st.warning("Pendiente de revisión.")

elif menu == "Mentores":
    st.markdown('<h1 class="main-title">Panel Mentores</h1>', unsafe_allow_html=True)
    if not st.session_state['auth_mentor']:
        with st.form("login_m"):
            u, p = st.text_input("Correo Mentor"), st.text_input("Clave", type="password")
            if st.form_submit_button("Ingresar"):
                m_ref = db.collection("authorized_mentors").document(u).get()
                if m_ref.exists and str(m_ref.to_dict().get('password')) == p:
                    st.session_state['auth_mentor'] = True
                    st.rerun()
                else: st.error("Acceso denegado.")
    else:
        pending = db.collection("queries").where(filter=FieldFilter("status", "==", "pending")).get()
        if not pending: st.info("No hay consultas pendientes.")
        for doc in pending:
            q = doc.to_dict()
            with st.container():
                st.markdown(f'<div class="card"><b>De: {q.get("student_email")}</b><br>{q.get("text")}</div>', unsafe_allow_html=True)
                ans = st.text_area("Respuesta:", key=doc.id)
                if st.button("Enviar Respuesta 📩", key=f"b_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status": "responded", "mentor_reply": ans})
                    enviar_notificacion(q.get("student_email"), ans, q.get("text"))
                    st.rerun()

elif menu == "Administrador":
    if not st.session_state['auth_mentor']:
        st.warning("🔒 Acceso exclusivo para Mentores.")
    else:
        st.markdown('<h1 class="main-title">Dashboard Administrativo</h1>', unsafe_allow_html=True)
        data = db.collection("queries").get()
        if data:
            df = pd.DataFrame([d.to_dict() for d in data])
            
            # --- CORRECCIÓN DE MÉTRICAS ---
            if 'status' not in df.columns: df['status'] = 'pending'
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Consultas Totales", len(df))
            col2.metric("Atendidos (Responded)", len(df[df['status'] == 'responded']))
            col3.metric("Pendientes (Pending)", len(df[df['status'] == 'pending']))
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.bar(df, x="campus", title="Sedes", color="campus", template="plotly_dark"), width="stretch")
            with c2:
                if 'career' in df.columns:
                    df['career'] = df['career'].fillna("Sin datos")
                    st.plotly_chart(px.bar(df, x="career", title="Carreras", color="career", template="plotly_dark"), width="stretch")

st.sidebar.caption("IdeaLabM3 v7.5 | UCV 2026")

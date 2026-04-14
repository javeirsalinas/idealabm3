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
        font-size: 3.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
    }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 1.5rem; margin-bottom: 1rem;
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
# 3. FUNCIÓN DE EMAIL
# ==========================================
def enviar_notificacion(destinatario, respuesta, duda_original):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASS"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "💡 IdeaLabM3: Tu mentor ha respondido"
        cuerpo = f"<html><body><div style='background:#f4f7f9;padding:20px;'><h2>Respuesta de IdeaLabM3</h2><p><b>Duda:</b> {duda_original}</p><hr><p><b>Asesoría:</b> {respuesta}</p></div></body></html>"
        msg.attach(MIMEText(cuerpo, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error de correo: {e}")
        return False

# ==========================================
# 4. NAVEGACIÓN
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    menu = option_menu("Menú", ["IdeaLabM3", "Estudiantes", "Mentores", "Administrador"], 
                       icons=['house', 'mortarboard', 'person-check', 'graph-up'], default_index=0)

# ==========================================
# 5. SECCIONES
# ==========================================

if menu == "IdeaLabM3":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Panel Estudiantil</h1>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with t1:
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            with col1:
                n, e, p = st.text_input("Nombre"), st.text_input("Correo"), st.text_input("Clave", type="password")
            with col2:
                s, ca = st.selectbox("Sede", CAMPUS_UCV), st.selectbox("Carrera", CARRERAS_UCV)
            if st.form_submit_button("Registrar Perfil"):
                db.collection("students").document(e).set({"name":n, "email":e, "password":p, "campus":s, "career":ca})
                st.success("¡Perfil guardado!")

    with t2:
        with st.form("q_form", clear_on_submit=True):
            user_mail = st.text_input("Confirma tu correo")
            duda_txt = st.text_area("Tu duda técnica")
            if st.form_submit_button("Enviar a Mentores 📩"):
                u_doc = db.collection("students").document(user_mail).get()
                if u_doc.exists:
                    udata = u_doc.to_dict()
                    db.collection("queries").add({
                        "student_email": user_mail,
                        "campus": udata.get('campus', 'No especificada'),
                        "career": udata.get('career', 'No especificada'),
                        "text": duda_txt, "status": "pending", "createdAt": datetime.now()
                    })
                    st.success("Consulta enviada.")
                else: st.error("Regístrate primero.")

    with t3:
        ver_m = st.text_input("Correo para respuestas")
        if ver_m:
            qs = db.collection("queries").where(filter=FieldFilter("student_email", "==", ver_m)).get()
            for doc in qs:
                q = doc.to_dict()
                with st.expander(f"Consulta: {q['text'][:30]}..."):
                    st.write(q['text'])
                    if 'mentor_reply' in q: st.info(f"Respuesta: {q['mentor_reply']}")

elif menu == "Mentores":
    st.markdown('<h1 class="main-title">Panel Mentores</h1>', unsafe_allow_html=True)
    if not st.session_state['authenticated']:
        with st.form("login"):
            u, p = st.text_input("Correo"), st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar"):
                m_ref = db.collection("authorized_mentors").document(u).get()
                if m_ref.exists and str(m_ref.to_dict().get('password')) == p:
                    st.session_state['authenticated'] = True
                    st.rerun()
    else:
        # Uso de FieldFilter para evitar UserWarning
        pending = db.collection("queries").where(filter=FieldFilter("status", "==", "pending")).get()
        for doc in pending:
            q = doc.to_dict()
            with st.container():
                st.markdown(f'<div class="card"><b>De: {q.get("student_email")}</b><br>{q.get("text")}</div>', unsafe_allow_html=True)
                ans = st.text_area("Respuesta:", key=doc.id)
                if st.button("Enviar 📩", key=f"b_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status": "responded", "mentor_reply": ans})
                    enviar_notificacion(q.get("student_email"), ans, q.get("text"))
                    st.rerun()

elif menu == "Administrador":
    if not st.session_state['authenticated']:
        st.warning("Inicia sesión en Mentores.")
    else:
        st.markdown('<h1 class="main-title">Dashboard</h1>', unsafe_allow_html=True)
        data = db.collection("queries").get()
        if data:
            df = pd.DataFrame([d.to_dict() for d in data])
            if 'career' in df.columns: df['career'] = df['career'].fillna("Sin datos")
            
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.bar(df, x="campus", title="Sedes", color="campus", template="plotly_dark"), width="stretch")
            with c2:
                if 'career' in df.columns:
                    st.plotly_chart(px.bar(df, x="career", title="Carreras", color="career", template="plotly_dark"), width="stretch")

st.sidebar.caption("IdeaLabM3 v7.0 | UCV 2026")

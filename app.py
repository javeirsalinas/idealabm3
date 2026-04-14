import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from streamlit_option_menu import option_menu
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
            st.error(f"Error de Conexión Firebase: {e}")
            return None
    return firestore.client()

db = get_db()

CAMPUS_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Arquitectura", "Medicina Humana", "Ciencias de la Comunicación", "Educación"]

# ==========================================
# 3. FUNCIÓN DE NOTIFICACIÓN POR EMAIL
# ==========================================
def enviar_notificacion(destinatario, respuesta, duda_original):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASS"]
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "💡 IdeaLabM3: Tu mentor ha respondido"
        cuerpo = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 15px;">
                    <h2 style="color: #004d99;">¡Hola! Tienes una nueva asesoría en IdeaLabM3</h2>
                    <p><b>Tu duda original:</b><br><i>"{duda_original}"</i></p>
                    <div style="background: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #00f2fe; margin: 20px 0;">
                        <p><b>Respuesta del Mentor:</b><br>{respuesta}</p>
                    </div>
                    <p>Sigue trabajando en tu proyecto. ¡Muchos éxitos!</p>
                    <p>Saludos,<br><b>Equipo de Emprendimiento UCV</b></p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(cuerpo, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except: return False

# ==========================================
# 4. NAVEGACIÓN
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
    except: pass
    return False

with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
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
# 5. CONTENIDO
# ==========================================

if menu == "IdeaLabM3":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Donde las ideas convergen</p>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Estudiantes</h1>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with t1:
        with st.form("reg_est"):
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
                    st.success("¡Perfil creado!")
                else: st.warning("Completa los datos.")

    with t2:
        with st.form("con_form", clear_on_submit=True):
            mail = st.text_input("Confirma tu correo")
            duda = st.text_area("Escribe tu consulta")
            if st.form_submit_button("Enviar 📩"):
                user_doc = db.collection("students").document(mail).get()
                if user_doc.exists:
                    udata = user_doc.to_dict()
                    db.collection("queries").add({
                        "student_email": mail, 
                        "campus": udata.get('campus', 'Lima'), 
                        "career": udata.get('career', 'Sistemas'),
                        "text": duda, "status": "pending", "createdAt": datetime.now()
                    })
                    st.success("¡Consulta enviada!")
                else: st.error("Regístrate primero.")

    with t3:
        ver_m = st.text_input("Correo para ver respuestas")
        if ver_m:
            consultas = db.collection("queries").where("student_email", "==", ver_m).get()
            for doc in consultas:
                q = doc.to_dict()
                with st.expander(f"Consulta: {q['text'][:40]}..."):
                    st.write(f"**Pregunta:** {q['text']}")
                    if 'mentor_reply' in q: st.info(f"**Mentor:** {q['mentor_reply']}")

elif menu == "Mentores":
    st.markdown('<h1 class="main-title">Panel Mentores</h1>', unsafe_allow_html=True)
    if not st.session_state['authenticated']:
        with st.form("login"):
            u, p = st.text_input("Correo"), st.text_input("Clave", type="password")
            if st.form_submit_button("Entrar"):
                if check_login(u, p): st.rerun()
                else: st.error("Error.")
    else:
        docs = db.collection("queries").where("status", "==", "pending").get()
        if not docs: st.info("Sin pendientes.")
        for doc in docs:
            q = doc.to_dict()
            with st.container():
                st.markdown(f'<div class="card"><b>De: {q.get("student_email")}</b><br>{q["text"]}</div>', unsafe_allow_html=True)
                ans = st.text_area("Respuesta:", key=doc.id)
                if st.button("Enviar y Notificar 📩", key=f"btn_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status": "responded", "mentor_reply": ans, "repliedAt": datetime.now()})
                    enviar_notificacion(q.get("student_email"), ans, q.get("text"))
                    st.rerun()

elif menu == "Administrador":
    if not st.session_state['authenticated']:
        st.warning("Acceso restringido a Mentores.")
    else:
        st.markdown('<h1 class="main-title">Dashboard Administrativo</h1>', unsafe_allow_html=True)
        q_docs = db.collection("queries").get()
        if q_docs:
            df = pd.DataFrame([d.to_dict() for d in q_docs])
            
            # Métricas
            m1, m2, m3 = st.columns(3)
            m1.metric("Consultas Totales", len(df))
            m2.metric("Pendientes", len(df[df['status']=='pending']))
            m3.metric("Atendidos", len(df[df['status']=='responded']))
            
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.bar(df, x="campus", title="Distribución por Campus", color="campus", template="plotly_dark")
                st.plotly_chart(fig1, use_container_width=True)
            with col_b:
                fig2 = px.bar(df, x="career", title="Consultas por Carrera Profesional", color="career", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            fig3 = px.pie(df, names="status", title="Estado General de Atención", hole=0.5, template="plotly_dark")
            st.plotly_chart(fig3, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdealabM3 v6.6 | @UCV 2026")

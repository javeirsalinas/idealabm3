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
# 2. CONEXIÓN FIREBASE Y LISTAS
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
CICLOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

def es_correo_ucv(email):
    dominios_validos = ["@ucv.edu.pe", "@ucvvirtual.edu.pe"]
    return any(email.lower().endswith(dom) for dom in dominios_validos)

# ==========================================
# 3. LÓGICA DE SESIÓN
# ==========================================
if 'auth_user' not in st.session_state: st.session_state['auth_user'] = None
if 'auth_mentor' not in st.session_state: st.session_state['auth_mentor'] = False

# ==========================================
# 4. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    menu = option_menu("IdeaLabM3", ["Inicio", "Estudiantes", "Mentores", "Administrador"], 
                       icons=['house', 'mortarboard', 'person-check', 'graph-up'], default_index=0)
    
    if st.session_state['auth_user'] or st.session_state['auth_mentor']:
        if st.button("Cerrar Sesión"):
            st.session_state['auth_user'] = None
            st.session_state['auth_mentor'] = False
            st.rerun()

# ==========================================
# 5. SECCIONES
# ==========================================

if menu == "Inicio":
    st.markdown('<h1 class="main-title">IdeaLabM3</h1>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Panel Estudiantil</h1>', unsafe_allow_html=True)
    
    if st.session_state['auth_user'] is None:
        t_log, t_reg = st.tabs(["🔑 Ingresar", "📝 Registrarse"])
        
        with t_log:
            with st.form("login_est"):
                mail = st.text_input("Correo Institucional")
                pw = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar"):
                    u_ref = db.collection("students").document(mail).get()
                    if u_ref.exists and str(u_ref.to_dict().get('password')) == pw:
                        st.session_state['auth_user'] = u_ref.to_dict()
                        st.rerun()
                    else: st.error("Credenciales incorrectas")

        with t_reg:
            with st.form("reg_est"):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nombre Completo")
                    cor = st.text_input("Correo Institucional")
                    cla = st.text_input("Crea una Clave", type="password")
                with col2:
                    sed = st.selectbox("Sede", CAMPUS_UCV)
                    car = st.selectbox("Carrera Profesional", CARRERAS_UCV)
                    cic = st.selectbox("Ciclo Actual", CICLOS)
                
                if st.form_submit_button("Registrarme"):
                    if not es_correo_ucv(cor):
                        st.error("❌ Solo correos @ucv.edu.pe o @ucvvirtual.edu.pe")
                    elif nom and cor and cla:
                        db.collection("students").document(cor).set({
                            "name": nom, "email": cor, "password": cla, 
                            "campus": sed, "career": car, "cycle": cic
                        })
                        st.success("✅ Registro exitoso. Ahora puedes Ingresar.")
    else:
        st.info(f"Sesión: {st.session_state['auth_user']['name']} | {st.session_state['auth_user']['career']}")
        t_con, t_res = st.tabs(["🚀 Nueva Consulta", "📩 Mis Respuestas"])
        with t_con:
            with st.form("c_f", clear_on_submit=True):
                txt = st.text_area("¿Cuál es tu consulta?")
                if st.form_submit_button("Enviar"):
                    db.collection("queries").add({
                        "student_email": st.session_state['auth_user']['email'],
                        "campus": st.session_state['auth_user']['campus'],
                        "career": st.session_state['auth_user']['career'], # CRITICAL: Se guarda aquí
                        "cycle": st.session_state['auth_user']['cycle'],
                        "text": txt, "status": "pending", "createdAt": datetime.now()
                    })
                    st.success("Consulta enviada.")
        
        with t_res:
            qs = db.collection("queries").where(filter=FieldFilter("student_email", "==", st.session_state['auth_user']['email'])).get()
            for doc in qs:
                q = doc.to_dict()
                with st.expander(f"Consulta: {q['text'][:30]}..."):
                    st.write(q['text'])
                    if 'mentor_reply' in q: st.info(f"Respuesta: {q['mentor_reply']}")

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
                st.markdown(f'<div class="card"><b>De: {q.get("student_email")} ({q.get("career")})</b><br>{q.get("text")}</div>', unsafe_allow_html=True)
                ans = st.text_area("Respuesta:", key=doc.id)
                if st.button("Enviar Respuesta 📩", key=f"b_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status": "responded", "mentor_reply": ans})
                    st.rerun()

elif menu == "Administrador":
    if not st.session_state['auth_mentor']:
        st.warning("Acceso exclusivo para mentores.")
    else:
        st.markdown('<h1 class="main-title">Dashboard Admin</h1>', unsafe_allow_html=True)
        docs = db.collection("queries").get()
        if docs:
            df = pd.DataFrame([d.to_dict() for d in docs])
            
            # --- LIMPIEZA Y VALIDACIÓN DE DATOS ---
            if 'career' not in df.columns:
                df['career'] = "No especificada"
            else:
                df['career'] = df['career'].fillna("No especificada")
            
            if 'campus' not in df.columns:
                df['campus'] = "No especificado"
            else:
                df['campus'] = df['campus'].fillna("No especificado")

            # Métricas
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Consultas", len(df))
            c2.metric("Atendidos", len(df[df['status'] == 'responded']))
            c3.metric("Pendientes", len(df[df['status'] == 'pending']))
            
            st.markdown("---")
            g1, g2 = st.columns(2)
            with g1:
                # Gráfico de Sedes
                fig_campus = px.bar(df, x="campus", title="Consultas por Sede", 
                                   template="plotly_dark", color="campus", width=None)
                st.plotly_chart(fig_campus, width="stretch")
            with g2:
                # Gráfico de Carreras (CORREGIDO)
                fig_career = px.bar(df, x="career", title="Consultas por Carrera", 
                                   template="plotly_dark", color="career", width=None)
                st.plotly_chart(fig_career, width="stretch")
            
            st.markdown("---")
            if 'cycle' in df.columns:
                fig_cycle = px.bar(df, x="cycle", title="Consultas por Ciclo", 
                                  template="plotly_dark", color="cycle", 
                                  category_orders={"cycle": CICLOS})
                st.plotly_chart(fig_cycle, width="stretch")

st.sidebar.caption("IdeaLabM3 v8.1 | UCV 2026")

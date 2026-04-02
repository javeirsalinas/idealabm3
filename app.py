import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from streamlit_option_menu import option_menu  # <--- Nueva Librería

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO "MISIÓN 3"
# ==========================================
st.set_page_config(
    page_title="IdeaLab M3 | Universidad César Vallejo",
    page_icon="💡",
    layout="wide",
)

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main-title {
        font-size: 3.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding: 1rem 0; margin-bottom: 1rem;
    }
    /* Estilo para los botones del menú */
    .nav-link { font-weight: 700 !important; }
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
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(79, 172, 254, 0.5); }
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
# 3. NAVEGACIÓN (BOTONES PREMIUM)
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=150)
    st.markdown("---")
    menu = option_menu(
        menu_title="Misión 3 Menú", 
        options=["Inicio", "Estudiantes", "Mentores", "Administrador"],
        icons=["house-door", "mortarboard", "people", "bar-chart-line"], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0a0a0a"},
            "icon": {"color": "#00f2fe", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#1a1a1a"},
            "nav-link-selected": {"background-color": "#4facfe", "color": "#050505"},
        }
    )

# Lógica de clasificación simple
def classify_query(text: str):
    t = text.lower()
    if any(w in t for w in ["negocio", "idea", "startup", "proyecto"]): return {"cat": "Emprendimiento"}
    if any(w in t for w in ["examen", "clase", "nota", "curso"]): return {"cat": "Académico"}
    return {"cat": "Otros"}

# Listas UCV
SEDES_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Contabilidad", "Derecho", "Psicología", "Ingeniería de Sistemas", "Ingeniería Industrial", "Ingeniería Civil", "Arquitectura", "Medicina Humana", "Enfermería"]

# ==========================================
# 4. CONTENIDO SEGÚN EL MENÚ
# ==========================================
st.markdown(f'<h1 class="main-title">IdeaLab M3: {menu}</h1>', unsafe_allow_html=True)

# --- INICIO ---
if menu == "Inicio":
    st.markdown("""
    <div class="card">
        <h2 style="color:#4facfe;">Impulsando el Talento Vallejiano 🚀</h2>
        <p>Bienvenido al ecosistema de innovación IdeaLab M3 de la <b>UCV</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

# --- ESTUDIANTES ---
elif menu == "Estudiantes":
    tab_reg, tab_query, tab_results = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with tab_reg:
        with st.form("reg"):
            name = st.text_input("Nombre")
            email = st.text_input("Correo Institucional")
            campus = st.selectbox("Sede", SEDES_UCV)
            career = st.selectbox("Carrera", CARRERAS_UCV)
            if st.form_submit_button("Registrarse"):
                db.collection("students").document(email).set({"name":name, "campus":campus, "career":career, "createdAt":datetime.now()})
                st.success("¡Perfil Creado!")

    with tab_query:
        student_email = st.text_input("Correo para validar")
        query_text = st.text_area("¿En qué te ayudamos?")
        if st.button("Enviar Mentoría"):
            if student_email and query_text:
                res = classify_query(query_text)
                db.collection("queries").add({"student_email":student_email, "text":query_text, "category":res['cat'], "status":"pending", "createdAt":datetime.now()})
                st.toast("Consulta enviada 🚀")

    with tab_results:
        check_email = st.text_input("Ingresa tu correo para ver respuestas")
        if check_email:
            docs = db.collection("queries").where("student_email", "==", check_email).get()
            for d in docs:
                q = d.to_dict()
                st.markdown(f'<div class="card"><span class="badge">{q["category"]}</span><p>{q["text"]}</p></div>', unsafe_allow_html=True)
                if q.get("mentor_reply"): st.info(f"Respuesta: {q['mentor_reply']}")

# --- MENTORES ---
elif menu == "Mentores":
    docs = db.collection("queries").where("status", "==", "pending").get()
    if not docs: st.info("No hay pendientes.")
    for doc in docs:
        q = doc.to_dict()
        with st.container():
            st.markdown(f'<div class="card"><h3>De: {q.get("student_email")}</h3><p>{q["text"]}</p></div>', unsafe_allow_html=True)
            with st.expander("Responder"):
                ans = st.text_area("Tu consejo:", key=doc.id)
                if st.button("Enviar", key=f"b_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status":"responded", "mentor_reply":ans, "repliedAt":datetime.now()})
                    st.rerun()

# --- ADMINISTRADOR ---
elif menu == "Administrador":
    q_docs = db.collection("queries").get()
    if q_docs:
        df = pd.DataFrame([d.to_dict() for d in q_docs])
        st.metric("Total Consultas", len(df))
        fig = px.pie(df, names="category", hole=0.5, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLab M3 v4.0 | @UCV 2026")

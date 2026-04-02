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
    /* Estilo para métricas */
    [data-testid="stMetricValue"] { color: #00f2fe !important; font-weight: 800; }
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
# 3. NAVEGACIÓN Y LISTAS
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = option_menu(
        menu_title="Misión 3 Menú", 
        options=["Inicio", "Estudiantes", "Mentores", "Administrador"],
        icons=["house", "mortarboard", "person-badge", "speedometer2"], 
        menu_icon="rocket", 
        default_index=0,
        styles={
            "container": {"background-color": "#0a0a0a", "padding": "5px"},
            "nav-link": {"color": "white", "font-size": "15px", "--hover-color": "#1a1a1a"},
            "nav-link-selected": {"background-color": "#4facfe", "color": "#050505"},
        }
    )

SEDES_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = ["Administración", "Administración en Turismo y Hotelería", "Contabilidad", "Economía", "Marketing y Dirección de Empresas", "Negocios Internacionales", "Derecho", "Psicología", "Ciencias de la Comunicación", "Educación Inicial", "Educación Primaria", "Medicina Humana", "Enfermería", "Nutrición y Dietética", "Obstetricia", "Ingeniería de Sistemas", "Ingeniería Industrial", "Ingeniería Civil", "Arquitectura", "Ciencias del Deporte", "Traducción e Interpretación", "Arte y Diseño Gráfico Empresarial"]

def classify_query(text: str):
    t = text.lower()
    if any(w in t for w in ["negocio", "idea", "startup", "proyecto"]): return {"cat": "Emprendimiento"}
    if any(w in t for w in ["examen", "clase", "nota", "curso"]): return {"cat": "Académico"}
    return {"cat": "Otros"}

# ==========================================
# 4. CONTENIDO POR SECCIÓN
# ==========================================
st.markdown(f'<h1 class="main-title">{menu}</h1>', unsafe_allow_html=True)

if menu == "IdeaLabM3":
    st.markdown('<div class="card"><h2>Impulsando el Talento Vallejiano 🚀</h2><p>Plataforma de Innovación IdeaLab M3.</p></div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

elif menu == "Estudiantes":
    tab_reg, tab_query, tab_results = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    with tab_reg:
        with st.form("reg"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre Completo")
                email = st.text_input("Correo Institucional")
            with col2:
                campus = st.selectbox("Sede", SEDES_UCV)
                career = st.selectbox("Carrera", CARRERAS_UCV)
            if st.form_submit_button("Crear Perfil"):
                db.collection("students").document(email).set({"name":name, "email":email, "campus":campus, "career":career, "createdAt":datetime.now()})
                st.success("¡Perfil Vallejiano Creado!")
    
    with tab_query:
        email_val = st.text_input("Confirma tu correo")
        text_q = st.text_area("¿Cuál es tu duda?")
        if st.button("Enviar"):
            res = classify_query(text_q)
            db.collection("queries").add({"student_email":email_val, "text":text_q, "category":res['cat'], "status":"pending", "createdAt":datetime.now()})
            st.toast("Enviado con éxito.")

    with tab_results:
        check = st.text_input("Ingresa tu correo para ver respuestas")
        if check:
            docs = db.collection("queries").where("student_email", "==", check).get()
            for d in docs:
                q = d.to_dict()
                st.markdown(f'<div class="card"><span class="badge">{q["category"]}</span><p>{q["text"]}</p></div>', unsafe_allow_html=True)
                if q.get("mentor_reply"): st.info(f"💡 Respuesta: {q['mentor_reply']}")

elif menu == "Mentores":
    docs = db.collection("queries").where("status", "==", "pending").get()
    if not docs: st.info("No hay consultas pendientes.")
    for doc in docs:
        q = doc.to_dict()
        with st.container():
            st.markdown(f'<div class="card"><h3>De: {q.get("student_email")}</h3><p>{q["text"]}</p></div>', unsafe_allow_html=True)
            with st.expander("Responder"):
                ans = st.text_area("Tu respuesta:", key=doc.id)
                if st.button("Enviar Mentoría", key=f"b_{doc.id}"):
                    db.collection("queries").document(doc.id).update({"status":"responded", "mentor_reply":ans, "repliedAt":datetime.now()})
                    st.rerun()

elif menu == "Administrador":
    # CARGA DE DATOS COMPLETA
    q_docs = db.collection("queries").get()
    s_docs = db.collection("students").get()
    
    if q_docs:
        # Convertir a DataFrame
        df_q = pd.DataFrame([d.to_dict() for d in q_docs])
        total_q = len(df_q)
        total_s = len(s_docs)
        resueltas = len(df_q[df_q['status'] == 'responded'])
        
        # FILA 1: MÉTRICAS
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Consultas Totales", total_q)
        with m2: st.metric("Estudiantes UCV", total_s)
        with m3: st.metric("Casos Resueltos", resueltas)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # FILA 2: GRÁFICOS
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.pie(df_q, names="category", title="Áreas de Interés", hole=0.5, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Cyan_r)
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.histogram(df_q, x="category", color="status", barmode="group", title="Estado por Categoría", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)
            
        # FILA 3: TABLA DE DATOS
        with st.expander("Ver lista detallada de consultas"):
            st.dataframe(df_q[['student_email', 'category', 'status', 'createdAt']], use_container_width=True)
    else:
        st.warning("No hay datos suficientes para generar el Dashboard aún.")

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLab M3 v4.1 | @UCV 2026")

import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from streamlit_option_menu import option_menu

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO PREMIUM
# ==========================================
st.set_page_config(
    page_title="IdeaLab M3 | Universidad César Vallejo",
    page_icon="💡",
    layout="wide",
)

# Inyección de CSS para Look & Feel Misión 3
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
# 3. NAVEGACIÓN Y LISTAS UCV
# ==========================================
with st.sidebar:
    st.image("https://www.ucv.edu.pe/wp-content/uploads/2020/01/logo-ucv.png", width=180)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = option_menu(
        menu_title="Misión 3 Menú", 
        options=["IdealabM3", "Estudiantes", "Mentores", "Administrador"],
        icons=["rocket-takeoff", "mortarboard", "person-badge", "speedometer2"], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"background-color": "#0a0a0a", "padding": "5px"},
            "nav-link": {"color": "white", "font-size": "15px", "--hover-color": "#1a1a1a"},
            "nav-link-selected": {"background-color": "#4facfe", "color": "#050505"},
        }
    )

SEDES_UCV = ["Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", "Chimbote", "Huaraz", "Trujillo", "Chepén", "Chiclayo", "Piura", "Tarapoto", "Moyobamba"]
CARRERAS_UCV = [
    "Administración", "Administración en Turismo y Hotelería", "Contabilidad", "Economía", 
    "Marketing y Dirección de Empresas", "Negocios Internacionales", "Derecho", "Psicología", 
    "Ciencias de la Comunicación", "Educación Inicial", "Educación Primaria", "Medicina Humana", 
    "Enfermería", "Nutrición y Dietética", "Obstetricia", "Ingeniería de Sistemas", 
    "Ingeniería Industrial", "Ingeniería Civil", "Arquitectura", "Ciencias del Deporte", 
    "Traducción e Interpretación", "Arte y Diseño Gráfico Empresarial"
]

def classify_query(text: str):
    t = text.lower()
    if any(w in t for w in ["negocio", "idea", "startup", "proyecto"]): return {"cat": "Emprendimiento"}
    if any(w in t for w in ["examen", "clase", "nota", "curso"]): return {"cat": "Académico"}
    return {"cat": "Otros"}

# ==========================================
# 4. CONTENIDO POR SECCIÓN
# ==========================================
st.markdown(f'<h1 class="main-title">{menu}</h1>', unsafe_allow_html=True)

# --- SECCIÓN: IdealabM3 (Antes Inicio) ---
if menu == "IdealabM3":
    st.markdown("""
    <div class="card">
        <h2 style="color:#4facfe;">Impulsando el Talento Vallejiano 🚀</h2>
        <p style="font-size:1.2rem;">
            Bienvenido a <b>IdealabM3</b>, el ecosistema de innovación de la <b>Universidad César Vallejo</b>. 
            Aquí transformamos tus ideas en proyectos reales con el apoyo de mentores expertos.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2070&auto=format&fit=crop")

# --- SECCIÓN: ESTUDIANTES ---
elif menu == "Estudiantes":
    tab_reg, tab_query, tab_results = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with tab_reg:
        with st.form("reg_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre Completo")
                email = st.text_input("Correo Institucional")
            with col2:
                campus = st.selectbox("Sede UCV", SEDES_UCV)
                career = st.selectbox("Carrera Profesional", CARRERAS_UCV)
            if st.form_submit_button("Crear Perfil"):
                if name and email:
                    db.collection("students").document(email).set({
                        "name":name, "email":email, "campus":campus, "career":career, "createdAt":datetime.now()
                    })
                    st.success(f"¡Bienvenido a IdealabM3, {name}!")

    with tab_query:
        email_val = st.text_input("Escribe tu correo para validar")
        text_q = st.text_area("Describe tu duda o proyecto")
        if st.button("Enviar a Mentoría"):
            if email_val and len(text_q) > 10:
                res = classify_query(text_q)
                db.collection("queries").add({
                    "student_email":email_val, "text":text_q, "category":res['cat'], 
                    "status":"pending", "createdAt":datetime.now(), "mentor_reply": ""
                })
                st.balloons()
                st.toast("Consulta enviada con éxito.")

    with tab_results:
        check = st.text_input("Ingresa tu correo para buscar respuestas")
        if check:
            docs = db.collection("queries").where("student_email", "==", check).get()
            if not docs: st.info("No se encontraron consultas para este correo.")
            for d in docs:
                q = d.to_dict()
                status_color = "#4facfe" if q['status'] == 'responded' else "#ff9f43"
                st.markdown(f"""
                <div class="card">
                    <span class="badge">{q['category']}</span>
                    <p><b>Tu consulta:</b> {q['text']}</p>
                    <p style="color:{status_color};"><b>Estado:</b> {q['status'].upper()}</p>
                </div>
                """, unsafe_allow_html=True)
                if q.get("mentor_reply"):
                    st.info(f"💡 Respuesta del Mentor: {q['mentor_reply']}")

# --- SECCIÓN: MENTORES ---
elif menu == "Mentores":
    docs = db.collection("queries").where("status", "==", "pending").get()
    if not docs:
        st.info("Bandeja de entrada vacía. ¡No hay consultas pendientes!")
    else:
        for doc in docs:
            q = doc.to_dict()
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <span class="badge">{q['category']}</span>
                    <h3>De: {q.get('student_email')}</h3>
                    <p>{q['text']}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("Responder Consulta"):
                    ans = st.text_area("Tu asesoría profesional:", key=doc.id)
                    if st.button("Enviar Respuesta", key=f"btn_{doc.id}"):
                        if ans:
                            db.collection("queries").document(doc.id).update({
                                "status":"responded", "mentor_reply":ans, "repliedAt":datetime.now()
                            })
                            st.toast("Respuesta enviada.")
                            st.rerun()

# --- SECCIÓN: ADMINISTRADOR ---
elif menu == "Administrador":
    q_docs = db.collection("queries").get()
    s_docs = db.collection("students").get()
    
    if q_docs:
        df_q = pd.DataFrame([d.to_dict() for d in q_docs])
        
        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric("Consultas Totales", len(df_q))
        m2.metric("Estudiantes Registrados", len(s_docs))
        m3.metric("Casos Resueltos", len(df_q[df_q['status'] == 'responded']))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.pie(df_q, names="category", title="Distribución por Áreas", hole=0.5, template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.histogram(df_q, x="category", color="status", barmode="group", title="Flujo de Trabajo", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)
            
        with st.expander("📋 Ver Base de Datos Completa"):
            st.dataframe(df_q, use_container_width=True)
    else:
        st.warning("Aún no hay datos registrados en el sistema.")

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLabM3 v4.2 | @UCV 2026")

import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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
        padding: 1.5rem 0; margin-bottom: 1rem;
    }
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px; padding: 1.8rem; margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    .card:hover { border: 1px solid rgba(79, 172, 254, 0.5); box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7); }
    .badge {
        display: inline-block; padding: 5px 15px; border-radius: 50px;
        font-size: 0.75rem; font-weight: 700; background: rgba(79, 172, 254, 0.15);
        color: #4facfe; text-transform: uppercase; margin-bottom: 12px;
        border: 1px solid rgba(79, 172, 254, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border: none; color: #050505 !important; font-weight: 800;
        border-radius: 14px; padding: 0.7rem 1.5rem; text-transform: uppercase;
        letter-spacing: 1.2px; transition: 0.4s; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(79, 172, 254, 0.5); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important; color: white !important;
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

def classify_query(text: str):
    t = text.lower()
    if any(w in t for w in ["negocio", "idea", "startup", "proyecto", "emprender"]):
        return {"cat": "Emprendimiento", "conf": 0.85}
    if any(w in t for w in ["examen", "clase", "nota", "curso", "tarea"]):
        return {"cat": "Académico", "conf": 0.90}
    if any(w in t for w in ["trabajo", "empleo", "cv", "bolsa"]):
        return {"cat": "Carrera", "conf": 0.80}
    return {"cat": "Otros", "conf": 0.50}

# ==========================================
# 3. LISTAS DE REFERENCIA UCV ACTUALIZADAS
# ==========================================
SEDES_UCV = [
    "Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", 
    "Chimbote", "Huaraz", "Trujillo", "Chepén", 
    "Chiclayo", "Piura", "Tarapoto", "Moyobamba"
]

CARRERAS_UCV = [
    "Administración", 
    "Administración en Turismo y Hotelería",
    "Contabilidad",
    "Economía",
    "Marketing y Dirección de Empresas",
    "Negocios Internacionales",
    "Derecho",
    "Psicología",
    "Ciencias de la Comunicación",
    "Educación Inicial",
    "Educación Primaria",
    "Medicina Humana",
    "Enfermería",
    "Nutrición y Dietética",
    "Obstetricia",
    "Ingeniería de Sistemas",
    "Ingeniería Industrial",
    "Ingeniería Civil",
    "Arquitectura",
    "Ciencias del Deporte",
    "Traducción e Interpretación",
    "Arte y Diseño Gráfico Empresarial"
]

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.markdown('<h1 class="main-title">IdeaLab M3 Platform</h1>', unsafe_allow_html=True)
menu = st.sidebar.radio("Navegación", ["🏠 Inicio", "🎓 Estudiantes", "🤝 Mentores", "📊 Administrador"])

# --- 🏠 INICIO ---
if menu == "🏠 Inicio":
    st.markdown("""
    <div class="card">
        <h2 style="color:#4facfe;">Impulsando el Talento Vallejiano 🚀</h2>
        <p style="font-size:1.1rem; color:#ccc;">
            Bienvenido a la plataforma de mentoría de la <b>Universidad César Vallejo</b>. 
            Conecta tus proyectos con expertos y lleva tu carrera al siguiente nivel siguiendo el ADN de <b>Misión 3</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=2070&auto=format&fit=crop")

# --- 🎓 ESTUDIANTES ---
elif menu == "🎓 Estudiantes":
    st.header("Portal del Estudiante")
    tab_reg, tab_query, tab_results = st.tabs(["📝 Registro", "🚀 Enviar Consulta", "📩 Mis Respuestas"])

    with tab_reg:
        with st.form("reg_student"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre Completo")
                email = st.text_input("Correo Institucional")
            with col2:
                campus = st.selectbox("Sede UCV", SEDES_UCV)
                career = st.selectbox("Carrera Profesional", CARRERAS_UCV)
            if st.form_submit_button("Crear mi Perfil"):
                if name and email:
                    db.collection("students").document(email).set({
                        "name": name, "email": email, "campus": campus, 
                        "career": career, "createdAt": datetime.now()
                    })
                    st.success(f"¡Perfil creado con éxito, {name}!")

    with tab_query:
        st.subheader("Cuéntanos tu idea")
        student_email = st.text_input("Valida tu correo institucional")
        query_text = st.text_area("¿Cómo podemos ayudarte hoy?", placeholder="Describe tu proyecto o duda académica...")
        if st.button("Enviar a Mentoría"):
            if len(query_text) > 10 and student_email:
                res = classify_query(query_text)
                db.collection("queries").add({
                    "student_email": student_email,
                    "text": query_text,
                    "category": res['cat'],
                    "status": "pending",
                    "mentor_reply": "",
                    "createdAt": datetime.now()
                })
                st.balloons()
                st.toast("Consulta enviada correctamente.")

    with tab_results:
        st.subheader("Tus Mentorías")
        check_email = st.text_input("Correo para buscar historial")
        if check_email:
            my_queries = db.collection("queries").where("student_email", "==", check_email).get()
            for q_doc in my_queries:
                q_data = q_doc.to_dict()
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <span class="badge">{q_data['category']}</span>
                        <p><b>Pregunta:</b> {q_data['text']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if q_data['status'] == 'responded':
                        st.info(f"💡 Mentoría: {q_data['mentor_reply']}")
                    else:
                        st.warning("⏳ Pendiente de revisión por un mentor.")

# --- 🤝 MENTORES ---
elif menu == "🤝 Mentores":
    st.markdown('<h2 style="color:#4facfe;">Panel de Gestión</h2>', unsafe_allow_html=True)
    docs = db.collection("queries").where("status", "==", "pending").order_by("createdAt").get()
    if not docs:
        st.info("No hay consultas nuevas. ✨")
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
                    reply = st.text_area("Tu consejo experto:", key=f"r_{doc.id}")
                    if st.button("Enviar Respuesta", key=f"b_{doc.id}"):
                        if reply:
                            db.collection("queries").document(doc.id).update({
                                "status": "responded", "mentor_reply": reply, "repliedAt": datetime.now()
                            })
                            st.rerun()

# --- 📊 ADMINISTRADOR ---
elif menu == "📊 Administrador":
    st.header("KPIs de Impacto")
    q_docs = db.collection("queries").get()
    s_docs = db.collection("students").get()
    if q_docs:
        df = pd.DataFrame([d.to_dict() for d in q_docs])
        col1, col2, col3 = st.columns(3)
        col1.metric("Consultas", len(df))
        col2.metric("Estudiantes", len(s_docs))
        col3.metric("Éxito (Resueltas)", len(df[df['status'] == 'responded']))
        
        c_a, c_b = st.columns(2)
        with c_a:
            fig = px.pie(df, names="category", title="Interés por Área", hole=0.5, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with c_b:
            # Gráfico por estado
            fig2 = px.histogram(df, x="category", color="status", barmode="group", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLab M3 v3.0 | UCV 2026")

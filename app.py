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

# Inyección de CSS Personalizado
st.markdown("""
    <style>
    /* Estética General Dark */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Título Principal con Gradiente Misión 3 */
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }

    /* Tarjetas Glassmorphism */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    .card:hover {
        border: 1px solid rgba(79, 172, 254, 0.5);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    }

    /* Badges / Etiquetas */
    .badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(79, 172, 254, 0.15);
        color: #4facfe;
        text-transform: uppercase;
        margin-bottom: 12px;
        border: 1px solid rgba(79, 172, 254, 0.3);
    }

    /* Botones Estilo Misión 3 */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border: none;
        color: #050505 !important;
        font-weight: 800;
        border-radius: 14px;
        padding: 0.7rem 1.5rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        transition: 0.4s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.5);
    }

    /* Inputs Dark */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN A FIREBASE Y LÓGICA DE IA
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
            st.error(f"Error de Configuración Firebase: {e}")
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
    if any(w in t for w in ["salud", "ayuda", "psicologo", "bienestar"]):
        return {"cat": "Bienestar", "conf": 0.75}
    return {"cat": "Otros", "conf": 0.50}

# ==========================================
# 3. LISTAS DE REFERENCIA UCV
# ==========================================
SEDES_UCV = [
    "Lima Norte", "Ate", "San Juan de Lurigancho", "Callao", 
    "Chimbote", "Huaraz", "Trujillo", "Chepén", 
    "Chiclayo", "Piura", "Tarapoto", "Moyobamba"
]

CARRERAS_UCV = [
    "Administración", "Arquitectura", "Ciencias de la Comunicación", 
    "Derecho", "Enfermería", "Ingeniería Civil", "Ingeniería de Sistemas", 
    "Ingeniería Industrial", "Medicina", "Psicología", "Contabilidad", "Educación"
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
        <h2 style="color:#4facfe;">Bienvenido Estudiante Vallejiano 🚀</h2>
        <p style="font-size:1.2rem; color:#ccc;">
            IdeaLab M3 es el espacio donde tus ideas se conectan con la mentoría experta. 
            Inspirado en la metodología de <b>Misión 3</b>, potenciamos tu talento UCV.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2070&auto=format&fit=crop", caption="Innovación y Tecnología en la UCV")

# --- 🎓 ESTUDIANTES ---
elif menu == "🎓 Estudiantes":
    st.header("Portal del Estudiante")
    tab_reg, tab_query, tab_results = st.tabs(["📝 Registro", "🚀 Enviar Consulta", "📩 Mis Respuestas"])

    with tab_reg:
        with st.form("reg_student"):
            st.markdown("### Datos Personales")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre Completo")
                email = st.text_input("Correo Institucional (@ucvvirtual.edu.pe)")
            with col2:
                campus = st.selectbox("Sede", SEDES_UCV)
                career = st.selectbox("Carrera", CARRERAS_UCV)
            
            if st.form_submit_button("Crear Perfil"):
                if name and email:
                    db.collection("students").document(email).set({
                        "name": name, "email": email, "campus": campus, 
                        "career": career, "createdAt": datetime.now()
                    })
                    st.success(f"¡Registro exitoso en la sede {campus}!")

    with tab_query:
        st.markdown("### ¿Cuál es tu próximo gran paso?")
        student_email = st.text_input("Escribe tu correo para validar")
        query_text = st.text_area("Cuéntanos tu duda o proyecto...", height=150)
        
        if st.button("Enviar Mentoría"):
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
                st.toast("Consulta enviada al ecosistema IdeaLab.")
            else:
                st.warning("Completa tu correo y describe bien tu idea.")

    with tab_results:
        check_email = st.text_input("Ingresa tu correo para ver el historial")
        if check_email:
            my_queries = db.collection("queries").where("student_email", "==", check_email).get()
            if not my_queries:
                st.info("No tienes consultas registradas con este correo.")
            for q_doc in my_queries:
                q_data = q_doc.to_dict()
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <span class="badge">{q_data['category']}</span>
                        <p><b>Pregunta:</b> {q_data['text']}</p>
                        <p style="color:#4facfe;"><b>Estado:</b> {q_data['status'].upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if q_data['status'] == 'responded':
                        st.info(f"💡 Mentoría: {q_data['mentor_reply']}")

# --- 🤝 MENTORES ---
elif menu == "🤝 Mentores":
    st.markdown('<h2 style="color:#4facfe;">Panel de Mentoría Experta</h2>', unsafe_allow_html=True)
    docs = db.collection("queries").where("status", "==", "pending").order_by("createdAt").get()
    
    if not docs:
        st.info("No hay consultas pendientes por el momento. ✨")
    else:
        for doc in docs:
            q = doc.to_dict()
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <span class="badge">{q['category']}</span>
                    <h3>Estudiante: {q.get('student_email')}</h3>
                    <p style="font-size:1.1rem;">{q['text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Redactar Respuesta de Mentoría"):
                    reply_text = st.text_area("Tu asesoría:", key=f"rep_{doc.id}")
                    if st.button("Enviar Respuesta Final", key=f"btn_{doc.id}"):
                        if reply_text:
                            db.collection("queries").document(doc.id).update({
                                "status": "responded",
                                "mentor_reply": reply_text,
                                "repliedAt": datetime.now()
                            })
                            st.toast("Mentoría registrada.")
                            st.rerun()

# --- 📊 ADMINISTRADOR ---
elif menu == "📊 Administrador":
    st.header("Métricas de Impacto UCV")
    q_docs = db.collection("queries").get()
    s_docs = db.collection("students").get()
    
    if q_docs:
        df = pd.DataFrame([d.to_dict() for d in q_docs])
        col1, col2, col3 = st.columns(3)
        col1.metric("Consultas Totales", len(df))
        col2.metric("Estudiantes UCV", len(s_docs))
        col3.metric("Resueltas", len(df[df['status'] == 'responded']))

        c_a, c_b = st.columns(2)
        with c_a:
            fig = px.pie(df, names="category", title="Interés por Categoría", hole=0.5, color_discrete_sequence=px.colors.sequential.Cyan_r)
            st.plotly_chart(fig, use_container_width=True)
        with c_b:
            fig2 = px.bar(df, x="category", color="status", title="Flujo de Trabajo", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLab M3 v2.8 | @UCV 2026")

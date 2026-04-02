import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
# ==========================================
st.set_page_config(
    page_title="IdeaLab M3 | Universidad César Vallejo",
    page_icon="💡",
    layout="wide",
)

# Estilo Premium CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px; padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px); margin-bottom: 1.5rem;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: 600;
        background: linear-gradient(90deg, #3b82f6, #2563eb); color: white;
        border: none; padding: 0.6rem; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN A FIREBASE Y LÓGICA DE IA
# ==========================================
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

def classify_query(text: str):
    t = text.lower()
    if any(w in t for w in ["negocio", "idea", "startup", "proyecto", "emprender"]):
        return {"cat": "Emprendimiento", "conf": 0.85}
    if any(w in t for w in ["examen", "clase", "nota", "curso", "tarea"]):
        return {"cat": "Academico", "conf": 0.90}
    if any(w in t for w in ["trabajo", "empleo", "cv", "bolsa"]):
        return {"cat": "Carrera", "conf": 0.80}
    if any(w in t for w in ["salud", "ayuda", "psicologo", "bienestar"]):
        return {"cat": "Bienestar", "conf": 0.75}
    return {"cat": "Otros", "conf": 0.50}

db = get_db()

# ==========================================
# 3. INTERFAZ PRINCIPAL (NAVEGACIÓN)
# ==========================================
st.markdown('<h1 class="main-title">IdeaLab M3 Platform</h1>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navegación", ["🏠 Inicio", "🎓 Estudiantes", "🤝 Mentores", "📊 Administrador"])

# --- 🏠 INICIO ---
if menu == "🏠 Inicio":
    st.markdown("""
    <div class="card">
        <h2>Bienvenido al Ecosistema IdeaLab M3 🚀</h2>
        <p>Selecciona tu perfil en el menú lateral para comenzar. Esta plataforma conecta 
        ideas con expertos y monitorea el impacto en tiempo real.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80")

# --- 🎓 ESTUDIANTES ---
elif menu == "🎓 Estudiantes":
    st.header("Portal del Estudiante")
    tab_reg, tab_query = st.tabs(["📝 Registro", "🚀 Enviar Consulta"])

    with tab_reg:
        with st.form("reg_student"):
            name = st.text_input("Nombre Completo")
            email = st.text_input("Correo Institucional")
            campus = st.selectbox("Sede", ["Los Olivos", "SJL", "Ate", "Chorrillos", "Trujillo", "Piura"])
            career = st.text_input("Carrera")
            if st.form_submit_button("Registrarse"):
                if name and email:
                    db.collection("students").add({"name": name, "email": email, "campus": campus, "career": career, "createdAt": datetime.now()})
                    st.success(f"¡Bienvenido {name}!")

    with tab_query:
        query_text = st.text_area("¿En qué te podemos ayudar?", placeholder="Explica tu idea o problema...")
        if st.button("Analizar y Enviar"):
            if len(query_text) > 10:
                res = classify_query(query_text)
                db.collection("queries").add({
                    "text": query_text, "category": res['cat'], "confidence": res['conf'],
                    "status": "pending", "createdAt": datetime.now()
                })
                st.success(f"Consulta enviada. Clasificada como: **{res['cat']}**")
                st.balloons()

# --- 🤝 MENTORES ---
elif menu == "🤝 Mentores":
    st.header("Panel de Gestión de Mentorías")
    docs = db.collection("queries").where("status", "==", "pending").get()
    if not docs:
        st.info("No hay consultas pendientes.")
    else:
        for doc in docs:
            q = doc.to_dict()
            with st.expander(f"Consulta: {q['category']} - {q.get('studentName', 'Estudiante')}"):
                st.write(f"**Texto:** {q['text']}")
                if st.button("Atender Consulta", key=doc.id):
                    db.collection("queries").document(doc.id).update({"status": "in_progress", "attendedAt": datetime.now()})
                    st.rerun()

# --- 📊 ADMINISTRADOR ---
elif menu == "📊 Administrador":
    st.header("Tablero de Control (KPIs)")
    q_docs = db.collection("queries").get()
    s_docs = db.collection("students").get()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Consultas Totales", len(q_docs))
    c2.metric("Estudiantes Activos", len(s_docs))
    c3.metric("Pendientes", len([d for d in q_docs if d.to_dict()['status'] == 'pending']))

    if q_docs:
        df = pd.DataFrame([d.to_dict() for d in q_docs])
        fig = px.pie(df, names="category", title="Distribución por Áreas", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = px.bar(df, x="category", color="status", title="Estado de Consultas por Categoría")
        st.plotly_chart(fig2, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLab M3 v2.0 | UCV")

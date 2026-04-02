import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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
    .stApp { background-color: #0d1117; color: #ffffff; }
    .main-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px; padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px); margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: 600;
        background: linear-gradient(90deg, #3b82f6, #2563eb); color: white;
        border: none; padding: 0.6rem; transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN A FIREBASE Y LÓGICA
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
        <h2>Bienvenido al Ecosistema IdeaLab M3 🚀</h2>
        <p>Plataforma exclusiva para la comunidad de la <b>Universidad César Vallejo</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80")

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
                campus = st.selectbox("Sede", SEDES_UCV)
                career = st.selectbox("Carrera", CARRERAS_UCV)
            
            if st.form_submit_button("Registrarse"):
                if name and email:
                    db.collection("students").document(email).set({
                        "name": name, "email": email, "campus": campus, 
                        "career": career, "createdAt": datetime.now()
                    })
                    st.success(f"¡Bienvenido {name} de la sede {campus}!")

    with tab_query:
        st.subheader("Nueva Mentoría")
        student_email = st.text_input("Confirma tu correo para enviar")
        query_text = st.text_area("¿En qué te podemos ayudar?", placeholder="Explica tu idea o problema...")
        
        if st.button("Enviar a IdeaLab"):
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
                st.success(f"Consulta enviada. Clasificada como: {res['cat']}")
                st.balloons()

    with tab_results:
        st.subheader("Seguimiento de mis consultas")
        check_email = st.text_input("Ingresa tu correo para ver tus respuestas")
        if check_email:
            my_queries = db.collection("queries").where("student_email", "==", check_email).get()
            if not my_queries:
                st.info("Aún no tienes consultas registradas.")
            for q_doc in my_queries:
                q_data = q_doc.to_dict()
                with st.expander(f"Consulta: {q_data['category']} - Estado: {q_data['status']}"):
                    st.write(f"**Tu pregunta:** {q_data['text']}")
                    if q_data['status'] == 'responded':
                        st.success(f"**Respuesta del Mentor:** {q_data['mentor_reply']}")
                    else:
                        st.warning("El mentor aún está revisando tu caso.")

# --- 🤝 MENTORES ---
elif menu == "🤝 Mentores":
    st.header("Panel de Gestión de Mentorías")
    docs = db.collection("queries").where("status", "==", "pending").get()
    
    if not docs:
        st.info("No hay consultas pendientes. ✨")
    else:
        for doc in docs:
            q = doc.to_dict()
            with st.expander(f"📥 Consulta de: {q.get('student_email')}"):
                st.write(f"**Mensaje:** {q['text']}")
                reply_text = st.text_area("Escribe tu asesoría aquí:", key=f"rep_{doc.id}")
                
                if st.button("Enviar Respuesta", key=f"btn_{doc.id}"):
                    if reply_text:
                        db.collection("queries").document(doc.id).update({
                            "status": "responded",
                            "mentor_reply": reply_text,
                            "repliedAt": datetime.now()
                        })
                        st.rerun()

# --- 📊 ADMINISTRADOR ---
elif menu == "📊 Administrador":
    st.header("KPIs de Impacto UCV")
    q_docs = db.collection("queries").get()
    s_docs = db.collection("students").get()
    
    if q_docs:
        df = pd.DataFrame([d.to_dict() for d in q_docs])
        c1, c2, c3 = st.columns(3)
        c1.metric("Consultas Totales", len(df))
        c2.metric("Estudiantes Registrados", len(s_docs))
        c3.metric("Casos Resueltos", len(df[df['status'] == 'responded']))

        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(df, names="category", title="Distribución por Áreas", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            # Aquí podrías cruzar datos con la sede si añades el campo a la consulta
            fig2 = px.histogram(df, x="category", color="status", barmode="group", title="Estado por Categoría")
            st.plotly_chart(fig2, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("IdeaLab M3 v2.5 | UCV")

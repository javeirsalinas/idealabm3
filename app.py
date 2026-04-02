import streamlit as st

# 1. Configuración de la Página
st.set_page_config(
    page_title="IdeaLab M3 Platform | UCV",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 2. Estilos CSS Personalizados (Vibrante y Moderno)
st.markdown("""
    <style>
    /* Fondo oscuro y tipografía premium */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
    }
    
    /* Gradiente para el Título Principal */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 2rem;
    }
    
    .subtitle {
        color: #9ca3af;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }

    /* Tarjetas de Contenido Estilo Glassmorphism */
    .premium-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Botones Estilizados */
    div.stButton > button {
        background: linear-gradient(90deg, #1e293b, #334155);
        color: white;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Contenido de la Pantalla de Bienvenida
st.markdown('<h1 class="main-title">IdeaLab M3</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ecosistema de Innovación, Emprendimiento y Bienestar</p>', unsafe_allow_html=True)

st.markdown("""
<div class="premium-card">
    <h3 style="color: #3b82f6; margin-top:0;">Bienvenido a la Nueva Experiencia 🚀</h3>
    <p style="font-size: 1.1rem; line-height: 1.6; color: #d1d5db;">
        Esta plataforma centraliza el apoyo académico y las mentorías de la UCV. 
        Gracias a la integración con <b>Streamlit + GitHub</b>, ahora el flujo de consultas 
        es más rápido, visual y eficiente.
    </p>
</div>
""", unsafe_allow_html=True)

# 4. Navegación por Roles
st.write("### 🧭 Selecciona tu Perfil")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🎓 Estudiantes")
    st.write("Registra tus ideas y recibe apoyo.")
    if st.button("Ir al Portal Estudiante", key="btn_est", use_container_width=True):
        st.info("👈 Selecciona **'1_Estudiante'** en la barra lateral.")

with col2:
    st.markdown("#### 🤝 Expertos")
    st.write("Gestiona tutorías y mentorías.")
    if st.button("Ir al Panel Mentor", key="btn_men", use_container_width=True):
        st.info("👈 Selecciona **'2_Mentor'** en la barra lateral.")

with col3:
    st.markdown("#### 📊 Gestión")
    st.write("Tablero de Analítica y KPIs.")
    if st.button("Ver Métricas Admin", key="btn_adm", use_container_width=True):
        st.info("👈 Selecciona **'3_Administrador'** en la barra lateral.")

# 5. Footer Informativo
st.divider()
footer_col1, footer_col2 = st.columns([2, 1])

with footer_col1:
    st.caption("© 2026 IdeaLab M3 - Universidad César Vallejo")
with footer_col2:
    st.caption("Powered by Streamlit Cloud & Firebase")

elif menu == "Estudiantes":
    st.markdown('<h1 class="main-title">Estudiantes</h1>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["📝 Registro", "🚀 Nueva Consulta", "📩 Mis Respuestas"])
    
    with t1:
        st.markdown('<div class="card"><h3>Registro de Perfil</h3>', unsafe_allow_html=True)
        with st.form("reg_form"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Nombre Completo")
                e = st.text_input("Correo Institucional")
                p = st.text_input("Contraseña", type="password")
            with c2:
                s = st.selectbox("Campus UCV", CAMPUS_UCV)
                ca = st.selectbox("Carrera Profesional", CARRERAS_UCV)
            
            if st.form_submit_button("Finalizar Registro"):
                if n and e and p:
                    db.collection("students").document(e).set({
                        "name": n, "email": e, "password": p, 
                        "campus": s, "career": ca, "createdAt": datetime.now()
                    })
                    st.success(f"¡Registro exitoso, {n}!")
                else:
                    st.warning("Completa todos los campos.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="card"><h3>Enviar Nueva Consulta</h3>', unsafe_allow_html=True)
        # Usamos un formulario para asegurar que los datos se envíen juntos
        with st.form("consulta_form", clear_on_submit=True):
            correo_consulta = st.text_input("Confirma tu correo registrado")
            texto_consulta = st.text_area("Escribe tu duda o avance de proyecto aquí")
            enviar_btn = st.form_submit_button("Enviar a Mentores 📩")
            
            if enviar_btn:
                if correo_consulta and texto_consulta:
                    # 1. Buscar al estudiante para obtener su CAMPUS
                    student_doc = db.collection("students").document(correo_consulta).get()
                    
                    if student_doc.exists:
                        datos_estudiante = student_doc.to_dict()
                        campus_estudiante = datos_estudiante.get('campus', 'No especificado')
                        
                        # 2. Guardar la consulta con el campus vinculado
                        db.collection("queries").add({
                            "student_email": correo_consulta,
                            "campus": campus_estudiante,
                            "text": texto_consulta,
                            "status": "pending",
                            "createdAt": datetime.now()
                        })
                        st.success("¡Consulta enviada con éxito! Revisa la pestaña 'Mis Respuestas' pronto.")
                    else:
                        st.error("❌ Este correo no está registrado. Por favor, ve a la pestaña 'Registro' primero.")
                else:
                    st.warning("Por favor, rellena ambos campos.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        st.markdown('<h3>Historial de Asesorías</h3>', unsafe_allow_html=True)
        ver_correo = st.text_input("Ingresa tu correo para ver tus respuestas", key="check_res")
        if ver_correo:
            docs = db.collection("queries").where("student_email", "==", ver_correo).order_by("createdAt", direction=firestore.Query.DESCENDING).get()
            if docs:
                for doc in docs:
                    data = doc.to_dict()
                    with st.expander(f"Consulta: {data['text'][:50]}..."):
                        st.write(f"**Tu pregunta:** {data['text']}")
                        if 'mentor_reply' in data:
                            st.info(f"✅ **Respuesta del Mentor:** {data['mentor_reply']}")
                        else:
                            st.warning("⏳ Aún no hay respuesta del mentor.")
            else:
                st.info("No se encontraron consultas para este correo.")

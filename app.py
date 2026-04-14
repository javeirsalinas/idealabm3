elif menu == "Administrador":
    if not st.session_state['authenticated']:
        st.warning("Acceso restringido a Mentores.")
    else:
        st.markdown('<h1 class="main-title">Dashboard Administrativo</h1>', unsafe_allow_html=True)
        q_docs = db.collection("queries").get()
        
        if q_docs:
            # Convertimos a DataFrame
            df = pd.DataFrame([d.to_dict() for d in q_docs])
            
            # --- MÉTRICAS SUPERIORES ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Consultas Totales", len(df))
            
            # Validamos si existe la columna 'status' para las métricas
            if 'status' in df.columns:
                m2.metric("Pendientes", len(df[df['status']=='pending']))
                m3.metric("Atendidos", len(df[df['status']=='responded']))
            else:
                m2.metric("Pendientes", 0)
                m3.metric("Atendidos", 0)
            
            st.markdown("---")
            
            # --- GRÁFICOS ---
            col_a, col_b = st.columns(2)
            
            with col_a:
                # Gráfico de Campus
                if 'campus' in df.columns:
                    fig1 = px.bar(df, x="campus", title="Distribución por Campus", 
                                  color="campus", template="plotly_dark")
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("Aún no hay datos de Campus para mostrar.")

            with col_b:
                # Gráfico de Carreras (CON VALIDACIÓN PARA EVITAR EL VALUEERROR)
                if 'career' in df.columns:
                    # Llenamos los valores vacíos con "No especificado" para que no rompa el gráfico
                    df['career'] = df['career'].fillna("No especificado")
                    fig2 = px.bar(df, x="career", title="Consultas por Carrera Profesional", 
                                  color="career", template="plotly_dark")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Aún no hay datos de Carreras. Las nuevas consultas aparecerán aquí.")
            
            st.markdown("---")
            
            # Gráfico de Pastel de Estado
            if 'status' in df.columns:
                fig3 = px.pie(df, names="status", title="Estado General de Atención", 
                              hole=0.5, template="plotly_dark")
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No hay consultas registradas en la base de datos.")

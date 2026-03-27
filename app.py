# ----------------------------
# SIDEBAR MENU LIMPO (SEM ERRO)
# ----------------------------
st.sidebar.markdown("## Grupo Acelerador")
st.sidebar.markdown("---")

# estado inicial
if "pagina" not in st.session_state:
    st.session_state.pagina = "Colaborador"

pagina = st.session_state.pagina

# função botão com destaque
def botao_menu(nome, label):
    if st.session_state.pagina == nome:
        st.sidebar.markdown(
            f"""
            <div style="
                background-color:#374151;
                padding:10px;
                border-radius:8px;
                margin-bottom:6px;
                font-weight:600;
            ">
                {label}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.pagina = nome
            st.rerun()

# menu
botao_menu("Colaborador", "👤 Colaborador")
botao_menu("Enviar Nota Fiscal", "📄 Enviar Nota Fiscal")

pagina = st.session_state.pagina

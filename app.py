# ----------------------------
# SIDEBAR MENU LIMPO
# ----------------------------
st.sidebar.markdown("## Grupo Acelerador")
st.sidebar.markdown("---")

if "pagina" not in st.session_state:
    st.session_state.pagina = "Colaborador"

def menu_button(label, page_name):
    is_active = st.session_state.pagina == page_name

    style = """
        background-color: #374151;
        border: 1px solid #4b5563;
    """ if is_active else ""

    if st.sidebar.button(label, use_container_width=True):
        st.session_state.pagina = page_name
        st.rerun()

    # aplica estilo visual no botão ativo
    st.sidebar.markdown(
        f"""
        <style>
        div[data-testid="stSidebar"] button[kind="secondary"] {{
            border-radius: 8px;
            margin-bottom: 6px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# botões
menu_button("👤 Colaborador", "Colaborador")
menu_button("📄 Enviar Nota Fiscal", "Enviar Nota Fiscal")

pagina = st.session_state.pagina

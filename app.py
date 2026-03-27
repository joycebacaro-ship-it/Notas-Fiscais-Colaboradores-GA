import streamlit as st

# ----------------------------
# CONFIG
# ----------------------------

# ----------------------------
# ESTILO SIDEBAR
# ----------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #1f2937;
}
[data-testid="stSidebar"] * {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# ESTADO
# ----------------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "Colaborador"

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.markdown("""
### Sistema de Notas
<span style='font-size:12px; color:#9ca3af;'>Grupo Acelerador</span>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("---")

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

# MENU
botao_menu("Colaborador", "👤 Colaborador")
botao_menu("Enviar Nota Fiscal", "📄 Enviar Nota Fiscal")

# ----------------------------
# IMPORTAÇÃO SEGURA DAS PÁGINAS
# ----------------------------
try:
    from pages import colaboradores
except:
    colaboradores = None

# try futuro:
# from pages import notas

# ----------------------------
# ROTEAMENTO
# ----------------------------
if st.session_state.pagina == "Colaborador":
    if colaboradores:
        colaboradores.render()
    else:
        st.error("Página de colaboradores não encontrada")

elif st.session_state.pagina == "Enviar Nota Fiscal":
    st.title("Enviar Nota Fiscal")
    st.info("🚧 Em construção")

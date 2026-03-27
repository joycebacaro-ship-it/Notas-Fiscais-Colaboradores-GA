import streamlit as st

st.set_page_config(page_title="Sistema de Notas", layout="wide")

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

.menu-item {
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 5px;
    font-weight: 500;
}

.menu-item:hover {
    background-color: #374151;
}

.menu-active {
    background-color: #374151;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# CONTROLE DE PÁGINA
# ----------------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "Colaborador"

pagina = st.session_state.pagina

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.markdown("## Grupo Acelerador")
st.sidebar.markdown("---")

colab_active = "menu-active" if pagina == "Colaborador" else ""
nota_active = "menu-active" if pagina == "Enviar Nota Fiscal" else ""

# botão colaborador
if st.sidebar.button("👤 Colaborador", use_container_width=True):
    st.session_state.pagina = "Colaborador"
    st.rerun()

st.sidebar.markdown(
    f'<div class="menu-item {colab_active}">👤 Colaborador</div>',
    unsafe_allow_html=True
)

# botão nota
if st.sidebar.button("📄 Enviar Nota Fiscal", use_container_width=True):
    st.session_state.pagina = "Enviar Nota Fiscal"
    st.rerun()

st.sidebar.markdown(
    f'<div class="menu-item {nota_active}">📄 Enviar Nota Fiscal</div>',
    unsafe_allow_html=True
)

# ----------------------------
# IMPORTAÇÃO DAS PÁGINAS
# ----------------------------
from pages import colaboradores

# (quando criar)
# from pages import notas

# ----------------------------
# ROTEAMENTO
# ----------------------------
if st.session_state.pagina == "Colaborador":
    colaboradores.render()

elif st.session_state.pagina == "Enviar Nota Fiscal":
    st.title("Enviar Nota Fiscal")
    st.info("🚧 Em construção")

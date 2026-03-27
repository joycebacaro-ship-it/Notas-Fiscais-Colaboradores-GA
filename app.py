import streamlit as st

st.set_page_config(page_title="Sistema de Notas", layout="wide")

# ----------------------------
# SIDEBAR ESCURA
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

st.sidebar.markdown("## Grupo Acelerador")

pagina = st.sidebar.radio(
    "",
    ["Colaborador", "Enviar Nota Fiscal"]
)

# ----------------------------
# IMPORTAÇÃO DAS PÁGINAS
# ----------------------------
from pages import colaboradores

# ----------------------------
# ROTEAMENTO
# ----------------------------
if pagina == "Colaborador":
    colaboradores.render()

elif pagina == "Enviar Nota Fiscal":
    st.title("Enviar Nota Fiscal")
    st.write("Em construção")

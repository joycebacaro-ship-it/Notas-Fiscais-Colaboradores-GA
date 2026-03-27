import streamlit as st

# ----------------------------
# CONFIG
# ----------------------------
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
# IMPORTAÇÃO DAS PÁGINAS
# ----------------------------
from pages import colaboradores
from pages import notas

# ----------------------------
# ROTEAMENTO CORRETO
# ----------------------------
if st.session_state.pagina == "Colaborador":
    colaboradores.render()

elif st.session_state.pagina == "Enviar Nota Fiscal":
    notas.render()

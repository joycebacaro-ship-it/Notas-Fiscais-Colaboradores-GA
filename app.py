# ----------------------------
# SIDEBAR PROFISSIONAL
# ----------------------------
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            background-color: #0E1117;
            color: white;
        }

        .menu-titulo {
            font-size: 14px;
            color: #9CA3AF;
            margin-top: 20px;
            margin-bottom: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Logo_example.svg/512px-Logo_example.svg.png", width=140)

    st.markdown("###")

    st.markdown("### 📊 Dashboard")
    st.markdown("### 💰 Oportunidades")
    st.markdown("### 👥 Contatos")

    st.markdown('<div class="menu-titulo">OPERACIONAL</div>', unsafe_allow_html=True)

    pagina = st.radio(
        "",
        ["📄 Enviar Nota Fiscal", "👤 Colaborador"]
    )

    st.markdown('<div class="menu-titulo">ANÁLISE</div>', unsafe_allow_html=True)

    st.markdown("### 📈 Estatísticas")
    st.markdown("### 🧠 BI")

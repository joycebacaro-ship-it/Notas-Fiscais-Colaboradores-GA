import streamlit as st
import pandas as pd
from datetime import datetime
import os

def render():

    st.markdown("""
    <style>
    .bloco {
        max-width: 900px;
        margin-left: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="bloco">', unsafe_allow_html=True)

    st.title("Enviar Nota Fiscal")

    # ----------------------------
    # ARQUIVOS
    # ----------------------------
    ARQUIVO_COLAB = "colaboradores.csv"
    ARQUIVO_NOTAS = "notas.csv"
    PASTA_NOTAS = "notas"

    if not os.path.exists(PASTA_NOTAS):
        os.makedirs(PASTA_NOTAS)

    if not os.path.exists(ARQUIVO_NOTAS):
        df_init = pd.DataFrame(columns=[
            "ID", "Colaborador", "Email", "Arquivo", "Data Upload"
        ])
        df_init.to_csv(ARQUIVO_NOTAS, index=False)

    # ----------------------------
    # VALIDAR COLABORADORES
    # ----------------------------
    if not os.path.exists(ARQUIVO_COLAB):
        st.error("Cadastre colaboradores antes de enviar notas")
        return

    df_colab = pd.read_csv(ARQUIVO_COLAB)

    if df_colab.empty:
        st.warning("Nenhum colaborador cadastrado")
        return

    lista_colab = df_colab["Nome"].tolist()

    # ----------------------------
    # MODAL
    # ----------------------------
    @st.dialog("Novo envio de Nota Fiscal")
    def modal_nota():

        colaborador = st.selectbox("Colaborador", ["Selecione"] + lista_colab)
        arquivo = st.file_uploader("Nota Fiscal (PDF)", type=["pdf"])

        if st.button("Enviar Nota"):

            if colaborador == "Selecione" or arquivo is None:
                st.error("Preencha todos os campos")
                return

            dados = df_colab[df_colab["Nome"] == colaborador].iloc[0]
            email = dados["Email"]

            df_notas = pd.read_csv(ARQUIVO_NOTAS)

            if df_notas.empty:
                novo_id = 1
            else:
                novo_id = int(df_notas["ID"].max()) + 1

            nome_arquivo = f"NF_{novo_id}_{arquivo.name}"
            caminho = os.path.join(PASTA_NOTAS, nome_arquivo)

            with open(caminho, "wb") as f:
                f.write(arquivo.getbuffer())

            nova_linha = {
                "ID": novo_id,
                "Colaborador": colaborador,
                "Email": email,
                "Arquivo": nome_arquivo,
                "Data Upload": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df_notas = pd.concat([df_notas, pd.DataFrame([nova_linha])], ignore_index=True)
            df_notas.to_csv(ARQUIVO_NOTAS, index=False)

            st.success("Nota enviada com sucesso!")
            st.rerun()

    # ----------------------------
    # BOTÃO ABRIR MODAL
    # ----------------------------
    if st.button("➕ Enviar nova nota"):
        modal_nota()

    # ----------------------------
    # TABELA
    # ----------------------------
    st.subheader("Notas enviadas")

    df_notas = pd.read_csv(ARQUIVO_NOTAS)

    if not df_notas.empty:
        df_notas = df_notas.sort_values(by="ID", ascending=False)
        st.dataframe(df_notas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma nota enviada ainda")

    st.markdown('</div>', unsafe_allow_html=True)

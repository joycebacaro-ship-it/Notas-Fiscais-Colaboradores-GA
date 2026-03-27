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

    # cria pasta se não existir
    if not os.path.exists(PASTA_NOTAS):
        os.makedirs(PASTA_NOTAS)

    # cria base de notas se não existir
    if not os.path.exists(ARQUIVO_NOTAS):
        df_init = pd.DataFrame(columns=[
            "ID", "Colaborador", "Email", "Arquivo", "Data Upload"
        ])
        df_init.to_csv(ARQUIVO_NOTAS, index=False)

    # carregar colaboradores
    if not os.path.exists(ARQUIVO_COLAB):
        st.error("Cadastre colaboradores antes de enviar notas")
        return

    df_colab = pd.read_csv(ARQUIVO_COLAB)

    if df_colab.empty:
        st.warning("Nenhum colaborador cadastrado")
        return

    # ----------------------------
    # SELEÇÃO COLABORADOR
    # ----------------------------
    lista_colab = df_colab["Nome"].tolist()

    colaborador = st.selectbox("Colaborador", ["Selecione"] + lista_colab)

    # ----------------------------
    # UPLOAD
    # ----------------------------
    arquivo = st.file_uploader("Nota Fiscal (PDF)", type=["pdf"])

    # ----------------------------
    # BOTÃO
    # ----------------------------
    if st.button("Enviar Nota"):

        if colaborador == "Selecione" or arquivo is None:
            st.error("Preencha todos os campos")
            return

        # buscar dados do colaborador
        dados = df_colab[df_colab["Nome"] == colaborador].iloc[0]
        email = dados["Email"]

        # gerar ID
        df_notas = pd.read_csv(ARQUIVO_NOTAS)

        if df_notas.empty:
            novo_id = 1
        else:
            novo_id = int(df_notas["ID"].max()) + 1

        # salvar arquivo
        nome_arquivo = f"NF_{novo_id}_{arquivo.name}"
        caminho = os.path.join(PASTA_NOTAS, nome_arquivo)

        with open(caminho, "wb") as f:
            f.write(arquivo.getbuffer())

        # salvar registro
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

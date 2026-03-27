import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pdfplumber
import re

def extrair_dados_pdf(caminho):

    texto = ""

    try:
        with pdfplumber.open(caminho) as pdf:
            for pagina in pdf.pages:
                texto += pagina.extract_text() or ""
    except:
        return {
            "cnpj": "",
            "valor": "",
            "data": "",
            "numero": ""
        }

    cnpj = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
    valor = re.search(r"R\$\s?\d+[.,]\d{2}", texto)
    data = re.search(r"\d{2}/\d{2}/\d{4}", texto)
    numero = re.search(r"\b\d{5,}\b", texto)

    return {
        "cnpj": cnpj.group() if cnpj else "",
        "valor": valor.group() if valor else "",
        "data": data.group() if data else "",
        "numero": numero.group() if numero else ""
    }

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
            "ID", "Colaborador", "Email", "Arquivo",
            "Valor", "CNPJ", "Numero", "Data Nota", "Data Upload"
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
    # MODAL INTELIGENTE
    # ----------------------------
    @st.dialog("Novo envio de Nota Fiscal")
    def modal_nota():

        colaborador = st.selectbox("Colaborador", ["Selecione"] + lista_colab)
        arquivo = st.file_uploader("Nota Fiscal (PDF)", type=["pdf"])

        valor = ""
        cnpj = ""
        numero = ""
        data = ""

        if arquivo is not None:

            caminho_temp = f"temp_{arquivo.name}"

            with open(caminho_temp, "wb") as f:
                f.write(arquivo.getbuffer())

            dados = extrair_dados_pdf(caminho_temp)

            st.markdown("### 📄 Dados identificados automaticamente")

            valor = st.text_input("Valor", value=dados["valor"])
            cnpj = st.text_input("CNPJ", value=dados["cnpj"])
            numero = st.text_input("Número da Nota", value=dados["numero"])
            data = st.text_input("Data da Nota", value=dados["data"])

        if st.button("Confirmar envio"):

            if colaborador == "Selecione" or arquivo is None:
                st.error("Preencha todos os campos")
                return

            dados_colab = df_colab[df_colab["Nome"] == colaborador].iloc[0]
            email = dados_colab["Email"]

            df_notas = pd.read_csv(ARQUIVO_NOTAS)

            novo_id = 1 if df_notas.empty else int(df_notas["ID"].max()) + 1

            nome_arquivo = f"NF_{novo_id}_{arquivo.name}"
            caminho_final = os.path.join(PASTA_NOTAS, nome_arquivo)

            with open(caminho_final, "wb") as f:
                f.write(arquivo.getbuffer())

            nova_linha = {
                "ID": novo_id,
                "Colaborador": colaborador,
                "Email": email,
                "Arquivo": nome_arquivo,
                "Valor": valor,
                "CNPJ": cnpj,
                "Numero": numero,
                "Data Nota": data,
                "Data Upload": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df_notas = pd.concat([df_notas, pd.DataFrame([nova_linha])], ignore_index=True)
            df_notas.to_csv(ARQUIVO_NOTAS, index=False)

            st.success("Nota processada e salva com sucesso!")
            st.rerun()

    # ----------------------------
    # BOTÃO
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

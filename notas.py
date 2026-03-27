import streamlit as st
import pandas as pd
from datetime import datetime
import os

from utils_pdf import extrair_dados_pdf


def garantir_colunas_notas(arquivo):

    colunas = [
        "ID",
        "Data Solicitação",
        "Colaborador",
        "Departamento",
        "Gestor",
        "Email",
        "Arquivo",
        "Valor",
        "Razão Social",
        "CNPJ",
        "Número NF",
        "Data Emissão",
        "Competência",
        "Chave de Acesso",
        "Data Upload"
    ]

    if not os.path.exists(arquivo):
        df = pd.DataFrame(columns=colunas)
        df.to_csv(arquivo, index=False)
        return df

    df = pd.read_csv(arquivo)

    for c in colunas:
        if c not in df.columns:
            df[c] = ""

    df = df[colunas]
    df.to_csv(arquivo, index=False)

    return df


def render():

    st.subheader("Notas Fiscais")

    ARQUIVO_COLAB = "colaboradores.csv"
    ARQUIVO_NOTAS = "notas.csv"
    PASTA = "notas"

    if not os.path.exists(PASTA):
        os.makedirs(PASTA)

    if not os.path.exists(ARQUIVO_COLAB):
        st.error("Cadastre colaboradores primeiro")
        return

    df_colab = pd.read_csv(ARQUIVO_COLAB)

    if df_colab.empty:
        st.warning("Sem colaboradores")
        return

    df_notas = garantir_colunas_notas(ARQUIVO_NOTAS)

    lista = sorted(df_colab["Nome"].dropna().tolist())

    @st.dialog("Nova Nota Fiscal")
    def modal():

        colaborador = st.selectbox("Colaborador", ["Selecione"] + lista)
        arquivo = st.file_uploader("PDF", type=["pdf"])

        valor = ""
        cnpj = ""
        numero = ""
        data = ""
        razao = ""
        competencia = ""
        chave = ""

        if arquivo:

            temp = f"temp_{arquivo.name}"

            with open(temp, "wb") as f:
                f.write(arquivo.getbuffer())

            dados = extrair_dados_pdf(temp)

            valor = dados.get("valor", "")
            cnpj = dados.get("documento", "")
            numero = dados.get("numero_nf", "")
            data = dados.get("data_emissao", "")
            razao = dados.get("razao_social", "")
            competencia = dados.get("competencia", "")
            chave = dados.get("chave", "")

            st.markdown("### Dados identificados")

            valor = st.text_input("Valor", value=valor)
            razao = st.text_input("Razão Social", value=razao)
            cnpj = st.text_input("CNPJ", value=cnpj)
            numero = st.text_input("Número NF", value=numero)
            data = st.text_input("Data Emissão", value=data)
            competencia = st.text_input("Competência", value=competencia)
            chave = st.text_input("Chave", value=chave)

            if os.path.exists(temp):
                os.remove(temp)

        if st.button("Salvar"):

            if colaborador == "Selecione" or not arquivo:
                st.error("Preencha tudo")
                return

            dados = df_colab[df_colab["Nome"] == colaborador].iloc[0]

            novo_id = 1 if df_notas.empty else int(df_notas["ID"].max()) + 1

            nome = f"NF_{novo_id}_{arquivo.name}"
            caminho = os.path.join(PASTA, nome)

            with open(caminho, "wb") as f:
                f.write(arquivo.getbuffer())

            nova = {
                "ID": novo_id,
                "Data Solicitação": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Colaborador": colaborador,
                "Departamento": dados["Departamento"],
                "Gestor": dados["Gestor"],
                "Email": dados["Email"],
                "Arquivo": nome,
                "Valor": valor,
                "Razão Social": razao,
                "CNPJ": cnpj,
                "Número NF": numero,
                "Data Emissão": data,
                "Competência": competencia,
                "Chave de Acesso": chave,
                "Data Upload": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df_final = pd.concat([df_notas, pd.DataFrame([nova])], ignore_index=True)
            df_final.to_csv(ARQUIVO_NOTAS, index=False)

            st.success("Salvo com sucesso")
            st.rerun()

    if st.button("➕ Nova Nota"):
        modal()

    st.subheader("Notas")

    df_notas = garantir_colunas_notas(ARQUIVO_NOTAS)

    if not df_notas.empty:
        st.dataframe(df_notas.sort_values(by="ID", ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma nota ainda")

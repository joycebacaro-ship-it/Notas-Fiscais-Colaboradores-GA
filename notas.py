import streamlit as st
import pandas as pd
from datetime import datetime
import os

from utils_pdf import extrair_dados_pdf


# ----------------------------
# GARANTIR ESTRUTURA DO CSV
# ----------------------------
def garantir_colunas_notas(arquivo_notas):

    colunas_esperadas = [
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

    if not os.path.exists(arquivo_notas):
        df_init = pd.DataFrame(columns=colunas_esperadas)
        df_init.to_csv(arquivo_notas, index=False)
        return df_init

    df = pd.read_csv(arquivo_notas)

    for col in colunas_esperadas:
        if col not in df.columns:
            df[col] = ""

    df = df[colunas_esperadas]
    df.to_csv(arquivo_notas, index=False)

    return df


# ----------------------------
# RENDER
# ----------------------------
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

    st.subheader("Notas Fiscais")

    ARQUIVO_COLAB = "colaboradores.csv"
    ARQUIVO_NOTAS = "notas.csv"
    PASTA_NOTAS = "notas"

    if not os.path.exists(PASTA_NOTAS):
        os.makedirs(PASTA_NOTAS)

    # ----------------------------
    # VALIDAÇÃO
    # ----------------------------
    if not os.path.exists(ARQUIVO_COLAB):
        st.error("Cadastre colaboradores antes de enviar notas")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df_colab = pd.read_csv(ARQUIVO_COLAB)

    if df_colab.empty:
        st.warning("Nenhum colaborador cadastrado")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    df_notas = garantir_colunas_notas(ARQUIVO_NOTAS)

    lista_colab = sorted(df_colab["Nome"].dropna().tolist())

    # ----------------------------
    # MODAL
    # ----------------------------
    @st.dialog("Novo envio de Nota Fiscal")
    def modal_nota():

        colaborador = st.selectbox("Colaborador", ["Selecione"] + lista_colab)
        arquivo = st.file_uploader("Nota Fiscal (PDF)", type=["pdf"])

        valor = ""
        cnpj = ""
        numero_nf = ""
        data_emissao = ""
        razao_social = ""
        competencia = ""
        chave = ""

        if arquivo is not None:

            caminho_temp = f"temp_{arquivo.name}"

            with open(caminho_temp, "wb") as f:
                f.write(arquivo.getbuffer())

            dados = extrair_dados_pdf(caminho_temp)

            valor = dados.get("valor", "")
            cnpj = dados.get("documento", "")
            numero_nf = dados.get("numero_nf", "")
            data_emissao = dados.get("data_emissao", "")
            razao_social = dados.get("razao_social", "")
            competencia = dados.get("competencia", "")
            chave = dados.get("chave", "")

            st.markdown("### 📄 Dados identificados automaticamente")

            valor = st.text_input("Valor da Nota Fiscal", value=valor)
            razao_social = st.text_input("Razão Social", value=razao_social)
            cnpj = st.text_input("CNPJ / CPF", value=cnpj)
            numero_nf = st.text_input("Número da NF", value=numero_nf)
            data_emissao = st.text_input("Data da Emissão", value=data_emissao)
            competencia = st.text_input("Competência", value=competencia)
            chave = st.text_input("Chave de Acesso", value=chave)

            # limpa arquivo temporário
            if os.path.exists(caminho_temp):
                try:
                    os.remove(caminho_temp)
                except:
                    pass

        # ----------------------------
        # SALVAR
        # ----------------------------
        if st.button("Confirmar envio"):

            if colaborador == "Selecione" or arquivo is None:
                st.error("Preencha todos os campos")
                return

            dados_colab = df_colab[df_colab["Nome"] == colaborador].iloc[0]

            email = dados_colab["Email"]
            departamento = dados_colab["Departamento"]
            gestor = dados_colab["Gestor"]

            df_notas_atual = garantir_colunas_notas(ARQUIVO_NOTAS)

            novo_id = (
                1
                if df_notas_atual.empty
                else int(pd.to_numeric(df_notas_atual["ID"], errors="coerce").fillna(0).max()) + 1
            )

            nome_arquivo = f"NF_{novo_id}_{arquivo.name}"
            caminho_final = os.path.join(PASTA_NOTAS, nome_arquivo)

            with open(caminho_final, "wb") as f:
                f.write(arquivo.getbuffer())

            nova_linha = {
                "ID": novo_id,
                "Data Solicitação": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Colaborador": colaborador,
                "Departamento": departamento,
                "Gestor": gestor,
                "Email": email,
                "Arquivo": nome_arquivo,
                "Valor": valor,
                "Razão Social": razao_social,
                "CNPJ": cnpj,
                "Número NF": numero_nf,
                "Data Emissão": data_emissao,
                "Competência": competencia,
                "Chave de Acesso": chave,
                "Data Upload": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df_notas_atual = pd.concat(
                [df_notas_atual, pd.DataFrame([nova_linha])],
                ignore_index=True
            )

            df_notas_atual.to_csv(ARQUIVO_NOTAS, index=False)

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

    df_notas = garantir_colunas_notas(ARQUIVO_NOTAS)

    if not df_notas.empty:
        df_notas = df_notas.sort_values(by="ID", ascending=False)
        st.dataframe(df_notas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma nota enviada ainda")

    st.markdown('</div>', unsafe_allow_html=True)

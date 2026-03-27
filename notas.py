import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pdfplumber
import re

# ----------------------------
# EXTRAÇÃO PDF
# ----------------------------
def extrair_dados_pdf(caminho):

    texto = ""

    try:
        with pdfplumber.open(caminho) as pdf:
            for pagina in pdf.pages:
                texto += pagina.extract_text() or ""
    except:
        return {}

    # ----------------------------
    # CNPJ / CPF
    # ----------------------------
    doc = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
    if not doc:
        doc = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto)

    # ----------------------------
    # VALOR
    # ----------------------------
    valores = re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", texto)

    valor_final = ""
    if valores:
        valor_final = sorted(
            valores,
            key=lambda x: float(x.replace("R$", "").replace(".", "").replace(",", "."))
        )[-1]

    # ----------------------------
    # DATA EMISSÃO
    # ----------------------------
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
    data_final = datas[0] if datas else ""

    # ----------------------------
    # NUMERO NF (NFS-e)
    # ----------------------------
    numero_match = re.search(
        r"(?:Número da NFS-e)[\s:\-]*([0-9]+)",
        texto,
        re.IGNORECASE
    )

    if not numero_match:
        numero_match = re.search(r"(?:NF|Nota Fiscal)[^\d]*(\d+)", texto, re.IGNORECASE)

    if not numero_match:
        numero_match = re.search(r"\b\d{6,}\b", texto)

    numero = numero_match.group(1) if numero_match and numero_match.groups() else (numero_match.group() if numero_match else "")

    # ----------------------------
    # RAZÃO SOCIAL
    # ----------------------------
    razao_match = re.search(
        r"(?:Nome\s*/\s*Nome Empresarial|Nome Empresarial)[\s:\-]*([^\n]+)",
        texto,
        re.IGNORECASE
    )

    razao = razao_match.group(1).strip() if razao_match else ""

    # ----------------------------
    # COMPETÊNCIA
    # ----------------------------
    competencia_match = re.search(
        r"(?:Competência da NFS-e)[\s:\-]*([0-9]{2}/[0-9]{4})",
        texto,
        re.IGNORECASE
    )

    competencia = competencia_match.group(1) if competencia_match else ""

    # ----------------------------
    # CHAVE DE ACESSO
    # ----------------------------
    chave_match = re.search(
        r"(?:Chave de Acesso da NFS-e)[\s:\-]*([0-9]+)",
        texto,
        re.IGNORECASE
    )

    chave = chave_match.group(1) if chave_match else ""

    return {
        "documento": doc.group() if doc else "",
        "valor": valor_final,
        "data": data_final,
        "numero": numero,
        "razao": razao,
        "competencia": competencia,
        "chave": chave
    }

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
            numero_nf = dados.get("numero", "")
            data_emissao = dados.get("data", "")
            razao_social = dados.get("razao", "")
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

        # ----------------------------
        # CONFIRMAR
        # ----------------------------
        if st.button("Confirmar envio"):

            if colaborador == "Selecione" or arquivo is None:
                st.error("Preencha todos os campos")
                return

            dados_colab = df_colab[df_colab["Nome"] == colaborador].iloc[0]

            email = dados_colab["Email"]
            departamento = dados_colab["Departamento"]
            gestor = dados_colab["Gestor"]

            df_notas = pd.read_csv(ARQUIVO_NOTAS)

            novo_id = 1 if df_notas.empty else int(df_notas["ID"].max()) + 1

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

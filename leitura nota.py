import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pdfplumber
import re


# ----------------------------
# NORMALIZAÇÃO DE TEXTO
# ----------------------------
def limpar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n+", "\n", texto)
    return texto.strip()


def extrair_valor_apos_rotulo(texto: str, rotulo: str) -> str:
    """
    Procura o valor logo após um rótulo.
    Primeiro tenta na mesma linha.
    Depois tenta na próxima linha não vazia.
    """
    linhas = [linha.strip() for linha in texto.split("\n")]

    for i, linha in enumerate(linhas):
        if rotulo.lower() in linha.lower():
            partes = re.split(re.escape(rotulo), linha, flags=re.IGNORECASE)
            if len(partes) > 1:
                resto = partes[1].strip(" :-")
                if resto:
                    return resto

            for j in range(i + 1, min(i + 4, len(linhas))):
                valor = linhas[j].strip(" :-")
                if valor:
                    return valor

    return ""


def extrair_valor_por_regex(texto: str, padrao: str) -> str:
    match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


# ----------------------------
# EXTRAÇÃO PDF
# ----------------------------
def extrair_dados_pdf(caminho: str) -> dict:
    texto = ""

    try:
        with pdfplumber.open(caminho) as pdf:
            for pagina in pdf.pages:
                texto += (pagina.extract_text() or "") + "\n"
    except Exception:
        return {
            "documento": "",
            "valor": "",
            "data_emissao": "",
            "numero_nf": "",
            "razao_social": "",
            "competencia": "",
            "chave": ""
        }

    texto = limpar_texto(texto)

    # ----------------------------
    # CHAVE DE ACESSO
    # ----------------------------
    chave = extrair_valor_por_regex(
        texto,
        r"Chave de Acesso da NFS-e\s*([0-9]{20,})"
    )

    # fallback
    if not chave:
        chave = extrair_valor_apos_rotulo(texto, "Chave de Acesso da NFS-e")
        chave_match = re.search(r"([0-9]{20,})", chave)
        chave = chave_match.group(1) if chave_match else ""

    # ----------------------------
    # NÚMERO DA NFS-e
    # ----------------------------
    numero_nf = extrair_valor_por_regex(
        texto,
        r"Número da NFS-e\s*([0-9]+)"
    )

    if not numero_nf:
        numero_nf = extrair_valor_apos_rotulo(texto, "Número da NFS-e")
        numero_match = re.search(r"([0-9]+)", numero_nf)
        numero_nf = numero_match.group(1) if numero_match else ""

    # ----------------------------
    # COMPETÊNCIA
    # na sua nota veio como data completa 01/12/2025
    # ----------------------------
    competencia = extrair_valor_por_regex(
        texto,
        r"Competência da NFS-e\s*([0-9]{2}/[0-9]{2}/[0-9]{4})"
    )

    if not competencia:
        competencia = extrair_valor_apos_rotulo(texto, "Competência da NFS-e")
        comp_match = re.search(r"([0-9]{2}/[0-9]{2}/[0-9]{4})", competencia)
        competencia = comp_match.group(1) if comp_match else ""

    # ----------------------------
    # DATA DA EMISSÃO DA NFS-e
    # precisa ser a da NFS-e, não da DPS
    # ----------------------------
    data_emissao = extrair_valor_por_regex(
        texto,
        r"Data da emissão da NFS-e\s*([0-9]{2}/[0-9]{2}/[0-9]{4})"
    )

    if not data_emissao:
        # fallback mais seguro, olhando o bloco específico
        linhas = [linha.strip() for linha in texto.split("\n")]
        for i, linha in enumerate(linhas):
            if "Data da emissão da NFS-e".lower() in linha.lower():
                for j in range(i + 1, min(i + 4, len(linhas))):
                    match = re.search(r"([0-9]{2}/[0-9]{2}/[0-9]{4})", linhas[j])
                    if match:
                        data_emissao = match.group(1)
                        break
                if data_emissao:
                    break

    # ----------------------------
    # RAZÃO SOCIAL
    # prioridade para o bloco do emitente
    # ----------------------------
    razao_social = ""

    linhas = [linha.strip() for linha in texto.split("\n")]
    for i, linha in enumerate(linhas):
        if "Nome / Nome Empresarial".lower() in linha.lower():
            # pega a próxima linha útil que não seja rótulo conhecido
            for j in range(i + 1, min(i + 6, len(linhas))):
                candidato = linhas[j].strip()
                if not candidato:
                    continue

                rotulos_ruins = [
                    "Inscrição Municipal",
                    "Regime",
                    "CEP",
                    "Município",
                    "CNPJ / CPF / NIF",
                    "E-mail",
                    "Telefone",
                    "Endereço",
                    "Tomador do Serviço",
                    "Prestador do Serviço"
                ]

                if any(r.lower() in candidato.lower() for r in rotulos_ruins):
                    continue

                # evita pegar e-mail
                if "@" in candidato:
                    continue

                razao_social = candidato
                break

            if razao_social:
                break

    # fallback
    if not razao_social:
        razao_social = extrair_valor_apos_rotulo(texto, "Nome / Nome Empresarial")
        if "@" in razao_social:
            razao_social = ""

    # ----------------------------
    # DOCUMENTO
    # prioridade para CNPJ / CPF / NIF do emitente
    # ----------------------------
    documento = ""
    for i, linha in enumerate(linhas):
        if "CNPJ / CPF / NIF".lower() in linha.lower():
            for j in range(i + 1, min(i + 4, len(linhas))):
                match = re.search(
                    r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})",
                    linhas[j]
                )
                if match:
                    documento = match.group(1)
                    break
            if documento:
                break

    # fallback global
    if not documento:
        match = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
        if match:
            documento = match.group(0)
        else:
            match = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto)
            documento = match.group(0) if match else ""

    # ----------------------------
    # VALOR LÍQUIDO DA NFS-e
    # prioridade absoluta
    # ----------------------------
    valor = extrair_valor_por_regex(
        texto,
        r"Valor Líquido da NFS-e\s*(R\$\s?\d{1,3}(?:\.\d{3})*,\d{2})"
    )

    if not valor:
        valor = extrair_valor_apos_rotulo(texto, "Valor Líquido da NFS-e")
        valor_match = re.search(r"(R\$\s?\d{1,3}(?:\.\d{3})*,\d{2})", valor)
        valor = valor_match.group(1) if valor_match else ""

    # fallback
    if not valor:
        valores = re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", texto)
        if valores:
            valor = sorted(
                valores,
                key=lambda x: float(x.replace("R$", "").replace(".", "").replace(",", "."))
            )[-1]

    return {
        "documento": documento,
        "valor": valor,
        "data_emissao": data_emissao,
        "numero_nf": numero_nf,
        "razao_social": razao_social,
        "competencia": competencia,
        "chave": chave
    }


# ----------------------------
# GARANTIR ESTRUTURA DO CSV
# ----------------------------
def garantir_colunas_notas(arquivo_notas: str) -> pd.DataFrame:
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

    for coluna in colunas_esperadas:
        if coluna not in df.columns:
            df[coluna] = ""

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

            if os.path.exists(caminho_temp):
                try:
                    os.remove(caminho_temp)
                except OSError:
                    pass

        if st.button("Confirmar envio"):
            if colaborador == "Selecione" or arquivo is None:
                st.error("Preencha todos os campos")
                return

            dados_colab = df_colab[df_colab["Nome"] == colaborador].iloc[0]

            email = dados_colab["Email"]
            departamento = dados_colab["Departamento"]
            gestor = dados_colab["Gestor"]

            df_notas_atual = garantir_colunas_notas(ARQUIVO_NOTAS)
            novo_id = 1 if df_notas_atual.empty else int(pd.to_numeric(df_notas_atual["ID"], errors="coerce").fillna(0).max()) + 1

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

    if st.button("➕ Enviar nova nota"):
        modal_nota()

    st.subheader("Notas enviadas")

    df_notas = garantir_colunas_notas(ARQUIVO_NOTAS)

    if not df_notas.empty:
        df_notas = df_notas.sort_values(by="ID", ascending=False)
        st.dataframe(df_notas, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma nota enviada ainda")

    st.markdown('</div>', unsafe_allow_html=True)

import pdfplumber
import re


def limpar_texto(texto):
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n+", "\n", texto)
    return texto.strip()


def extrair_dados_pdf(caminho):

    texto = ""

    try:
        with pdfplumber.open(caminho) as pdf:
            for pagina in pdf.pages:
                texto += (pagina.extract_text() or "") + "\n"
    except:
        return {}

    texto = limpar_texto(texto)

    linhas = texto.split("\n")

    # ----------------------------
    # CHAVE DE ACESSO
    # ----------------------------
    match_chave = re.search(
        r"Chave de Acesso da NFS-e\s*\n?\s*([0-9]{44})",
        texto,
        re.IGNORECASE
    )
    chave = match_chave.group(1) if match_chave else ""

    # ----------------------------
    # NÚMERO NF
    # ----------------------------
    match_numero = re.search(
        r"Número da NFS-e\s*\n?\s*([0-9]+)",
        texto,
        re.IGNORECASE
    )
    numero_nf = match_numero.group(1) if match_numero else ""

    # ----------------------------
    # COMPETÊNCIA
    # ----------------------------
    match_comp = re.search(
        r"Competência da NFS-e\s*\n?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})",
        texto,
        re.IGNORECASE
    )
    competencia = match_comp.group(1) if match_comp else ""

    # ----------------------------
    # DATA EMISSÃO
    # ----------------------------
    match_data = re.search(
        r"Data da emissão da NFS-e\s*\n?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})",
        texto,
        re.IGNORECASE
    )
    data_emissao = match_data.group(1) if match_data else ""

    # ----------------------------
    # RAZÃO SOCIAL (BLOCO PRESTADOR)
    # ----------------------------
    razao_social = ""

    inicio = None
    fim = None

    for i, linha in enumerate(linhas):
        if "Prestador do Serviço".lower() in linha.lower():
            inicio = i

        if "TOMADOR DO SERVIÇO".lower() in linha.lower():
            fim = i
            break

    if inicio is not None and fim is not None:

        bloco = linhas[inicio:fim]

        for i, linha in enumerate(bloco):
            if "Nome / Nome Empresarial".lower() in linha.lower():

                if i + 1 < len(bloco):
                    candidato = bloco[i + 1].strip()

                    if candidato and "@" not in candidato:
                        razao_social = candidato

                break

    # ----------------------------
    # CNPJ
    # ----------------------------
    match_cnpj = re.search(
        r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
        texto
    )
    cnpj = match_cnpj.group(0) if match_cnpj else ""

    # ----------------------------
    # VALOR LÍQUIDO
    # ----------------------------
    match_valor = re.search(
        r"Valor Líquido da NFS-e.*?(R\$\s?\d{1,3}(?:\.\d{3})*,\d{2})",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    valor = match_valor.group(1) if match_valor else ""

    if not valor:
        valores = re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", texto)
        if valores:
            valor = valores[-1]

    # ----------------------------
    # RETORNO FINAL
    # ----------------------------
    return {
        "documento": cnpj,
        "valor": valor,
        "data_emissao": data_emissao,
        "numero_nf": numero_nf,
        "razao_social": razao_social,
        "competencia": competencia,
        "chave": chave
    }

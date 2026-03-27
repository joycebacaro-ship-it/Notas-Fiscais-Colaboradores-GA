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
        r"\b\d{44}\b",
        texto
    )
    chave = match_chave.group(0) if match_chave else ""

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
    # RAZÃO SOCIAL (INTELIGENTE)
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
        encontrou_label = False

        for linha in bloco:

            if "Nome / Nome Empresarial".lower() in linha.lower():
                encontrou_label = True
                continue

            if encontrou_label:

                candidato = linha.strip()

                if not candidato:
                    continue

                # FILTROS
                if any(x in candidato.lower() for x in [
                    "cep", "rua", "avenida", "av", "município",
                    "telefone", "email", "inscrição", "endereço"
                ]):
                    continue

                if "@" in candidato:
                    continue

                if re.search(r"\d{5}-\d{3}", candidato):
                    continue

                # encontrou nome válido
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
    # VALOR
    # ----------------------------
    valor = ""

    for i, linha in enumerate(linhas):
        if "Valor Líquido da NFS-e".lower() in linha.lower():
            for j in range(i, i + 5):
                if j < len(linhas):
                    match = re.search(
                        r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}",
                        linhas[j]
                    )
                    if match:
                        valor = match.group(0)
                        break

    # fallback
    if not valor:
        valores = re.findall(
            r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}",
            texto
        )
        if valores:
            valor = valores[-1]

    # ----------------------------
    # RETORNO
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

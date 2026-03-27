import pdfplumber
import re


def limpar_texto(texto):
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n+", "\n", texto)
    return texto.strip()


def buscar_valor_abaixo(texto, rotulo, limite_linhas=5):
    linhas = texto.split("\n")

    for i, linha in enumerate(linhas):
        if rotulo.lower() in linha.lower():
            for j in range(i + 1, min(i + limite_linhas, len(linhas))):
                valor = linhas[j].strip()

                if not valor:
                    continue

                # ignora labels
                if any(x in valor.lower() for x in [
                    "cnpj", "telefone", "email", "endereço", "inscrição", "município"
                ]):
                    continue

                return valor

    return ""


def extrair_dados_pdf(caminho):

    texto = ""

    try:
        with pdfplumber.open(caminho) as pdf:
            for pagina in pdf.pages:
                texto += (pagina.extract_text() or "") + "\n"
    except:
        return {}

    texto = limpar_texto(texto)

    # ----------------------------
    # CHAVE DE ACESSO
    # ----------------------------
    chave = re.search(r"\b\d{44}\b", texto)
    chave = chave.group(0) if chave else ""

    # ----------------------------
    # NÚMERO DA NFS-e
    # ----------------------------
    numero_nf = buscar_valor_abaixo(texto, "Número da NFS-e")
    numero_nf = re.search(r"\d+", numero_nf).group(0) if numero_nf else ""

    # ----------------------------
    # COMPETÊNCIA
    # ----------------------------
    competencia = buscar_valor_abaixo(texto, "Competência da NFS-e")
    comp_match = re.search(r"\d{2}/\d{2}/\d{4}", competencia)
    competencia = comp_match.group(0) if comp_match else ""

    # ----------------------------
    # DATA EMISSÃO (corrigido)
    # ----------------------------
   data_emissao = ""

match_data = re.search(
    r"Data da emissão da NFS-e\s*\n?\s*([0-9]{2}/[0-9]{2}/[0-9]{4})",
    texto,
    re.IGNORECASE
)

if match_data:
    data_emissao = match_data.group(1)
    data_match = re.search(r"\d{2}/\d{2}/\d{4}", data_emissao)
    data_emissao = data_match.group(0) if data_match else ""

    # ----------------------------
    # RAZÃO SOCIAL (emitente)
    # ----------------------------
    razao = ""

    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        if "Prestador do Serviço".lower() in linha.lower():
            for j in range(i, i + 15):
                if j >= len(linhas):
                    break

                if "Nome / Nome Empresarial".lower() in linhas[j].lower():
                    for k in range(j + 1, j + 6):
                        if k >= len(linhas):
                            break

                        candidato = linhas[k].strip()

                        if not candidato:
                            continue

                        if any(x in candidato.lower() for x in [
                            "inscrição", "regime", "cep", "município",
                            "cnpj", "email", "telefone"
                        ]):
                            continue

                        if "@" in candidato:
                            continue

                        razao = candidato
                        break

                if razao:
                    break

        if razao:
            break

    # ----------------------------
    # CNPJ
    # ----------------------------
    cnpj = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
    cnpj = cnpj.group(0) if cnpj else ""

    # ----------------------------
    # VALOR LÍQUIDO
    # ----------------------------
    valor = ""

    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        if "Valor Líquido da NFS-e".lower() in linha.lower():
            for j in range(i, i + 5):
                if j >= len(linhas):
                    break

                match = re.search(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", linhas[j])
                if match:
                    valor = match.group(0)
                    break

    # fallback
    if not valor:
        valores = re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", texto)
        if valores:
            valor = valores[-1]

    return {
        "documento": cnpj,
        "valor": valor,
        "data_emissao": data_emissao,
        "numero_nf": numero_nf,
        "razao_social": razao,
        "competencia": competencia,
        "chave": chave
    }

import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Sistema de Notas", layout="wide")

# ----------------------------
# ESTILO
# ----------------------------
st.markdown(
    """
    <style>
    .bloco {
        max-width: 600px;
        margin-left: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="bloco">', unsafe_allow_html=True)

st.title("Sistema de Notas")
st.subheader("Cadastro de Colaboradores")

# ----------------------------
# ARQUIVO
# ----------------------------
ARQUIVO = "colaboradores.csv"

if not os.path.exists(ARQUIVO):
    df_inicial = pd.DataFrame(columns=[
        "ID", "Email", "Nome", "Departamento", "Gestor", "Status", "Data Cadastro"
    ])
    df_inicial.to_csv(ARQUIVO, index=False)

# ----------------------------
# CARREGAR DADOS
# ----------------------------
df = pd.read_csv(ARQUIVO)

# garantir ID
if "ID" not in df.columns:
    df["ID"] = range(1, len(df) + 1)
    df.to_csv(ARQUIVO, index=False)

# ----------------------------
# LISTAS
# ----------------------------
DEPARTAMENTOS_BASE = [
    "Assessoria Diretoria Executiva",
    "Comercial",
    "Compras",
    "Diretores Giants",
    "Diretoria Executiva",
    "Educação",
    "Estoque",
    "Eventos - Operação",
    "Eventos - Produção",
    "Eventos - Técnica",
    "Eventos Externos",
    "Experiência do Cliente",
    "Financeiro",
    "Gente e Gestão",
    "Infraestrutura",
    "Marketing - Criação",
    "Marketing - Performance",
    "Marketing - Redes Sociais",
    "Mentoria",
    "Merchandising",
    "Relacionamento",
    "Sucesso do Cliente",
    "Tecnologia da Informação",
    "XR"
    "Teste"
]

GESTORES_BASE = [
    "Alnilam Campos",
    "Diego Depardieu",
    "Vitor Damasceno",
    "Débora Castro",
    "Thais Silva",
    "Vinicius Franco",
    "Rodrigo Mourão",
    "Aline Marques",
    "Lucas Amaral",
    "Marcus Marques",
    "Liz Nunes",
    "Patricy Caetano",
    "Virginia Pierini",
    "Rafael Garcia",
    "Camila Távora",
    "Deyse Lima"
    "Teste"
]

DEPARTAMENTOS = ["Selecione"] + sorted(DEPARTAMENTOS_BASE)
GESTORES = ["Selecione"] + sorted(GESTORES_BASE)

# ----------------------------
# FORMULÁRIO
# ----------------------------
nome = st.text_input("Nome completo")
email = st.text_input("E-mail corporativo")

departamento = st.selectbox("Departamento", DEPARTAMENTOS)
gestor = st.selectbox("Gestor imediato", GESTORES)

ativo = st.checkbox("Ativo", value=True)

# ----------------------------
# BOTÃO
# ----------------------------
if st.button("Cadastrar"):
    if nome and email and departamento != "Selecione" and gestor != "Selecione":

        status = "Ativo" if ativo else "Inativo"

        if email in df["Email"].values:
            st.warning("Email já cadastrado.")
        else:
            if df.empty:
                novo_id = 1
            else:
                novo_id = int(df["ID"].max()) + 1

            nova_linha = {
                "ID": novo_id,
                "Email": email,
                "Nome": nome,
                "Departamento": departamento,
                "Gestor": gestor,
                "Status": status,
                "Data Cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            df.to_csv(ARQUIVO, index=False)

            st.success(f"Colaborador cadastrado com ID {novo_id}")

            # 🔥 RESET CORRETO
            st.rerun()

    else:
        st.error("Preencha todos os campos obrigatórios")

# ----------------------------
# TABELA
# ----------------------------
df = pd.read_csv(ARQUIVO)

st.subheader("Colaboradores cadastrados")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("Nenhum colaborador cadastrado ainda.")

st.markdown('</div>', unsafe_allow_html=True)

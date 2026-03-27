import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 🔥 LAYOUT WIDE (não centralizado)
st.set_page_config(page_title="Sistema de Notas", layout="wide")

# ----------------------------
# MARGEM + ALINHAMENTO ESQUERDA
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
# ARQUIVO DE DADOS
# ----------------------------
ARQUIVO = "colaboradores.csv"

if not os.path.exists(ARQUIVO):
    df_inicial = pd.DataFrame(columns=[
        "Email", "Nome", "Departamento", "Gestor", "Status", "Data Cadastro"
    ])
    df_inicial.to_csv(ARQUIVO, index=False)

# ----------------------------
# CARREGAR DADOS
# ----------------------------
df = pd.read_csv(ARQUIVO)

# ----------------------------
# LISTAS BASE
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
]

# ----------------------------
# ORDENAÇÃO
# ----------------------------
DEPARTAMENTOS = ["Selecione"] + sorted(DEPARTAMENTOS_BASE)
GESTORES = ["Selecione"] + sorted(GESTORES_BASE)

# ----------------------------
# CONTROLE DOS CAMPOS
# ----------------------------
if "nome" not in st.session_state:
    st.session_state.nome = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "gestor" not in st.session_state:
    st.session_state.gestor = "Selecione"

if "departamento" not in st.session_state:
    st.session_state.departamento = "Selecione"

if "ativo" not in st.session_state:
    st.session_state.ativo = True

# ----------------------------
# FORMULÁRIO
# ----------------------------
nome = st.text_input("Nome completo", key="nome")
email = st.text_input("E-mail corporativo", key="email")

departamento = st.selectbox(
    "Departamento",
    DEPARTAMENTOS,
    key="departamento"
)

gestor = st.selectbox(
    "Gestor imediato",
    GESTORES,
    key="gestor"
)

ativo = st.checkbox("Ativo", key="ativo")

# ----------------------------
# BOTÃO
# ----------------------------
if st.button("Cadastrar"):
    if nome and email and departamento != "Selecione" and gestor != "Selecione":

        status = "Ativo" if ativo else "Inativo"

        if email in df["Email"].values:
            st.warning("Email já cadastrado.")
        else:
            nova_linha = {
                "Email": email,
                "Nome": nome,
                "Departamento": departamento,
                "Gestor": gestor,
                "Status": status,
                "Data Cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            df.to_csv(ARQUIVO, index=False)

            st.success("Colaborador cadastrado com sucesso!")

            st.session_state.nome = ""
            st.session_state.email = ""
            st.session_state.gestor = "Selecione"
            st.session_state.departamento = "Selecione"
            st.session_state.ativo = True

    else:
        st.error("Preencha todos os campos obrigatórios")

# ----------------------------
# TABELA
# ----------------------------
st.subheader("Colaboradores cadastrados")

df = pd.read_csv(ARQUIVO)

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("Nenhum colaborador cadastrado ainda.")

st.markdown('</div>', unsafe_allow_html=True)

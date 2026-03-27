import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Sistema de Notas", layout="centered")

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
# LISTA DE DEPARTAMENTOS
# ----------------------------
DEPARTAMENTOS = [
    "Selecione",
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

# ----------------------------
# CONTROLE DOS CAMPOS
# ----------------------------
if "email" not in st.session_state:
    st.session_state.email = ""

if "nome" not in st.session_state:
    st.session_state.nome = ""

if "gestor" not in st.session_state:
    st.session_state.gestor = ""

if "departamento" not in st.session_state:
    st.session_state.departamento = "Selecione"

if "ativo" not in st.session_state:
    st.session_state.ativo = True

# ----------------------------
# FORMULÁRIO
# ----------------------------
email = st.text_input("Email corporativo", key="email")
nome = st.text_input("Nome completo", key="nome")

departamento = st.selectbox(
    "Departamento",
    DEPARTAMENTOS,
    key="departamento"
)

gestor = st.text_input("Gestor direto", key="gestor")

ativo = st.checkbox("Ativo", key="ativo")

# ----------------------------
# BOTÃO CADASTRAR
# ----------------------------
if st.button("Cadastrar"):
    if email and nome and departamento != "Selecione":

        status = "Ativo" if ativo else "Inativo"

        # valida duplicidade
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

            # limpar campos
            st.session_state.email = ""
            st.session_state.nome = ""
            st.session_state.gestor = ""
            st.session_state.departamento = "Selecione"
            st.session_state.ativo = True

    else:
        st.error("Preencha todos os campos obrigatórios")

# ----------------------------
# ATUALIZAR DADOS NA TELA
# ----------------------------
df = pd.read_csv(ARQUIVO)

# ----------------------------
# TABELA
# ----------------------------
st.subheader("Colaboradores cadastrados")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.write("Nenhum colaborador cadastrado ainda.")

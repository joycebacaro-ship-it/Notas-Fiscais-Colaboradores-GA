import streamlit as st
import pandas as pd

st.title("Sistema de Notas")

st.subheader("Cadastro de Colaboradores")

# cria memória (lista) se não existir
if "colaboradores" not in st.session_state:
    st.session_state.colaboradores = []

email = st.text_input("Email corporativo")
nome = st.text_input("Nome completo")

departamento = st.selectbox("Departamento", [
    "Marketing",
    "Comercial",
    "Financeiro",
    "Operações"
])

gestor = st.text_input("Gestor direto")

if st.button("Cadastrar"):
    if email and nome:
        novo = {
            "Email": email,
            "Nome": nome,
            "Departamento": departamento,
            "Gestor": gestor
        }

        st.session_state.colaboradores.append(novo)

        st.success("Colaborador cadastrado com sucesso!")
    else:
        st.error("Preencha os campos obrigatórios")

# 👇 MOSTRAR CADASTROS
st.subheader("Colaboradores cadastrados")

if st.session_state.colaboradores:
    df = pd.DataFrame(st.session_state.colaboradores)
    st.dataframe(df)
else:
    st.write("Nenhum colaborador cadastrado ainda.")

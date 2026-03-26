import streamlit as st

st.title("Sistema de Notas")

st.subheader("Cadastro de Colaboradores")

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
        st.success("Colaborador cadastrado com sucesso!")
    else:
        st.error("Preencha os campos obrigatórios")

import streamlit as st
import pandas as pd
from datetime import datetime
import os

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

    st.title("Sistema de Notas")
    st.subheader("Colaboradores")

    ARQUIVO = "colaboradores.csv"

    # criar arquivo se não existir
    if not os.path.exists(ARQUIVO):
        df_inicial = pd.DataFrame(columns=[
            "ID", "Email", "Nome", "Departamento", "Gestor", "Status", "Data Cadastro"
        ])
        df_inicial.to_csv(ARQUIVO, index=False)

    df = pd.read_csv(ARQUIVO)

    # garantir ID
    if "ID" not in df.columns:
        df["ID"] = range(1, len(df) + 1)
        df.to_csv(ARQUIVO, index=False)

    # ----------------------------
    # LISTAS
    # ----------------------------
    DEPARTAMENTOS = ["Selecione"] + sorted([
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
    ])

    GESTORES = ["Selecione"] + sorted([
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
    ])

    # ----------------------------
    # MODAL
    # ----------------------------
    @st.dialog("Novo Colaborador")
    def modal():

        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail corporativo")

        departamento = st.selectbox("Departamento", DEPARTAMENTOS)
        gestor = st.selectbox("Gestor imediato", GESTORES)

        ativo = st.checkbox("Ativo", value=True)

        if st.button("Salvar cadastro"):

            if nome and email and departamento != "Selecione" and gestor != "Selecione":

                if email in df["Email"].values:
                    st.warning("Email já cadastrado.")
                    return

                novo_id = 1 if df.empty else int(df["ID"].max()) + 1

                nova_linha = {
                    "ID": novo_id,
                    "Email": email,
                    "Nome": nome,
                    "Departamento": departamento,
                    "Gestor": gestor,
                    "Status": "Ativo" if ativo else "Inativo",
                    "Data Cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
                }

                df_novo = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                df_novo.to_csv(ARQUIVO, index=False)

                st.success("Cadastro realizado!")
                st.rerun()

            else:
                st.error("Preencha todos os campos")

    # botão abrir modal
    if st.button("➕ Criar cadastro"):
        modal()

    # ----------------------------
    # TABELA
    # ----------------------------
    st.subheader("Colaboradores cadastrados")

    df = pd.read_csv(ARQUIVO)

    if not df.empty:

        df = df.sort_values(by="ID", ascending=False)

        colunas = ["ID"] + [c for c in df.columns if c != "ID"]
        df = df[colunas]

        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.info("Nenhum colaborador cadastrado")

    st.markdown('</div>', unsafe_allow_html=True)

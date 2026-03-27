import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Sistema de Notas", layout="wide")

# ----------------------------
# MENU LATERAL
# ----------------------------
st.sidebar.title("Menu")

pagina = st.sidebar.radio(
    "Navegação",
    ["Enviar Nota Fiscal", "Colaborador"]
)

# ----------------------------
# ESTILO
# ----------------------------
st.markdown(
    """
    <style>
    .bloco {
        max-width: 900px;
        margin-left: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# PAGINA: COLABORADOR
# ============================
if pagina == "Colaborador":

    st.markdown('<div class="bloco">', unsafe_allow_html=True)

    st.title("Sistema de Notas")
    st.subheader("Colaboradores")

    # ----------------------------
    # ARQUIVO
    # ----------------------------
    ARQUIVO = "colaboradores.csv"

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

    DEPARTAMENTOS = ["Selecione"] + sorted(DEPARTAMENTOS_BASE)
    GESTORES = ["Selecione"] + sorted(GESTORES_BASE)

    # ----------------------------
    # MODAL
    # ----------------------------
    @st.dialog("Novo Colaborador")
    def modal_cadastro():

        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail corporativo")

        departamento = st.selectbox("Departamento", DEPARTAMENTOS)
        gestor = st.selectbox("Gestor imediato", GESTORES)

        ativo = st.checkbox("Ativo", value=True)

        if st.button("Salvar cadastro"):
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

                    df_novo = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                    df_novo.to_csv(ARQUIVO, index=False)

                    st.success("Cadastro realizado com sucesso!")
                    st.rerun()

            else:
                st.error("Preencha todos os campos obrigatórios")

    # botão abrir modal
    if st.button("➕ Criar cadastro"):
        modal_cadastro()

    # ----------------------------
    # TABELA
    # ----------------------------
    st.subheader("Colaboradores cadastrados")

    df = pd.read_csv(ARQUIVO)

    if not df.empty:

        df_exibir = df.copy()
        df_exibir = df_exibir.sort_values(by="ID", ascending=False)

        colunas = ["ID"] + [col for col in df_exibir.columns if col != "ID"]
        df_exibir = df_exibir[colunas]

        st.dataframe(df_exibir, use_container_width=True, hide_index=True)

    else:
        st.write("Nenhum colaborador cadastrado ainda.")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================
# PAGINA: NOTA FISCAL
# ============================
if pagina == "Enviar Nota Fiscal":

    st.title("Enviar Nota Fiscal")

    st.info("🚧 Em construção")

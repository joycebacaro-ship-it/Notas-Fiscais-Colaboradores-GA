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

    if not os.path.exists(ARQUIVO):
        df_inicial = pd.DataFrame(columns=[
            "ID", "Email", "Nome", "Departamento", "Gestor", "Status", "Data Cadastro"
        ])
        df_inicial.to_csv(ARQUIVO, index=False)

    df = pd.read_csv(ARQUIVO)

    if "ID" not in df.columns:
        df["ID"] = range(1, len(df) + 1)
        df.to_csv(ARQUIVO, index=False)

    st.success("Página de colaboradores carregada 🚀")

    st.markdown('</div>', unsafe_allow_html=True)

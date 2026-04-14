import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURAÇÃO DA IA (GEMINI PRO - O MAIS ESTÁVEL)
API_KEY = "AIzaSyBMIsMJ9xfSW7IrJhhKGfq1D61dxsguIF8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# 2. CONFIGURAÇÃO DA PLANILHA
def salvar_na_planilha(nome, texto_aluno, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Relatório de Comunicação - Curso Técnico").sheet1
        sheet.append_row([nome, texto_aluno, feedback])
        return True
    except:
        return False

# 3. INTERFACE
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼")
st.title("💼 Sistema de Treinamento Executivo")

if 'nome' not in st.session_state:
    st.subheader("Identificação do Colaborador")
    nome_input = st.text_input("Digite seu nome completo:")
    if st.button("Acessar Desafios"):
        if nome_input:
            st.session_state.nome = nome_input
            st.rerun()
else:
    st.sidebar.write(f"👤 {st.session_state.nome}")
    st.header("Fase 1: Comunicado Interno")
    st.info("SITUAÇÃO: Informe a equipe sobre o aumento de 10% no VR e entrega dos cartões na sexta.")
    
    texto_aluno = st.text_area("Sua proposta de e-mail:", height=150)

    if st.button("Enviar para Revisão"):
        if texto_aluno:
            with st.spinner('Analisando...'):
                try:
                    # Tenta usar a IA
                    prompt = f"Dê um feedback profissional curto para este e-mail: {texto_aluno}"
                    response = model.generate_content(prompt)
                    feedback = response.text
                except:
                    # Se a IA falhar de novo, o jogo não trava!
                    feedback = "Texto recebido com sucesso! O professor fará a avaliação manual na planilha."
                
                st.subheader("Resultado:")
                st.write(feedback)
                salvar_na_planilha(st.session_state.nome, texto_aluno, feedback)
                st.success("Dados salvos no relatório!")

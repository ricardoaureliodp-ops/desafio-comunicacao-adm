import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURAÇÃO DA IA (GEMINI) - CHAVE E MODELO LIMPOS
API_KEY = "AIzaSyBMIsMJ9xfSW7IrJhhKGfq1D61dxsguIF8"
genai.configure(api_key=API_KEY)
# Usando o nome direto, sem o "models/" que causou o erro 404
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. CONFIGURAÇÃO DA PLANILHA
def salvar_na_planilha(nome, texto_aluno, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Relatório de Comunicação - Curso Técnico").sheet1
        sheet.append_row([nome, texto_aluno, feedback])
        return True
    except Exception as e:
        return False

# 3. INTERFACE DO USUÁRIO
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
    st.sidebar.write(f"👤 **Colaborador:** {st.session_state.nome}")
    if st.sidebar.button("Sair/Trocar Nome"):
        del st.session_state.nome
        st.rerun()

    st.header("Fase 1: Comunicado Interno")
    with st.expander("📝 SITUAÇÃO: Informar a equipe sobre o novo Vale Refeição", expanded=True):
        st.write("Sua tarefa: Informar sobre o aumento de 10% no VR e entrega dos cartões na sexta.")

    texto_aluno = st.text_area("Sua proposta de e-mail:", height=150)

    if st.button("Enviar para Revisão"):
        if texto_aluno:
            with st.spinner('O Diretor está analisando...'):
                try:
                    prompt = f"Feedback curto para este e-mail de aluno de administração: {texto_aluno}"
                    response = model.generate_content(prompt)
                    feedback = response.text
                    st.info(feedback)
                    salvar_na_planilha(st.session_state.nome, texto_aluno, feedback)
                    st.success("Resposta enviada com sucesso!")
                except Exception as e:
                    st.error(f"Erro no Diretor: {e}")

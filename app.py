import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. IA (Gemini Pro)
API_KEY = "AIzaSyBMIsMJ9xfSW7IrJhhKGfq1D61dxsguIF8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# 2. FUNÇÃO DE SALVAR COM RELATÓRIO DE ERRO
def salvar_na_planilha(nome, texto, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        # Abre a planilha pelo nome exato
        sheet = client.open("Relatório de Comunicação - Curso Técnico").sheet1
        sheet.append_row([nome, texto, feedback])
        return True, "OK"
    except Exception as e:
        return False, str(e)

# 3. INTERFACE
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼")
if 'nome' not in st.session_state:
    st.title("Identificação")
    nome = st.text_input("Seu nome completo:")
    if st.button("Entrar"):
        if nome: st.session_state.nome = nome; st.rerun()
else:
    st.title(f"Desafio: {st.session_state.nome}")
    texto = st.text_area("Escreva seu e-mail profissional:", height=150)
    if st.button("Enviar para o Diretor"):
        with st.spinner('Analisando...'):
            try:
                res = model.generate_content(f"Feedback profissional curto: {texto}")
                feedback = res.text
            except:
                feedback = "O Diretor recebeu seu texto!"
            
            st.info(feedback)
            
            # TENTA SALVAR E MOSTRA O ERRO SE FALHAR
            sucesso, erro_msg = salvar_na_planilha(st.session_state.nome, texto, feedback)
            if sucesso:
                st.success("✅ SALVO NA PLANILHA DO PROFESSOR!")
            else:
                st.error(f"❌ ERRO AO SALVAR: {erro_msg}")

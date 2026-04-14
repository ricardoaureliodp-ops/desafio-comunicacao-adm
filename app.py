import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURAÇÃO DA IA (GEMINI)
# IMPORTANTE: Se você tiver sua própria chave, substitua o texto abaixo
API_KEY = "SUA_CHAVE_AQUI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 2. CONFIGURAÇÃO DA PLANILHA (GOOGLE SHEETS)
def salvar_na_planilha(nome, texto_aluno, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        # Abre a planilha pelo nome exato que você criou
        sheet = client.open("Relatório de Comunicação - Curso Técnico").sheet1
        sheet.append_row([nome, texto_aluno, feedback])
    except Exception as e:
        print(f"Erro ao salvar na planilha: {e}")

# 3. INTERFACE DO USUÁRIO (STREAMLIT)
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼")

st.title("💼 Sistema de Treinamento Executivo")

if 'nome' not in st.session_state:
    st.subheader("Identificação do Colaborador")
    nome_input = st.text_input("Digite seu nome completo para acessar os desafios:")
    if st.button("Acessar Desafios"):
        if nome_input:
            st.session_state.nome = nome_input
            st.rerun()
        else:
            st.warning("Por favor, digite seu nome.")
else:
    st.sidebar.write(f"👤 **Colaborador:** {st.session_state.nome}")
    if st.sidebar.button("Sair/Trocar Nome"):
        del st.session_state.nome
        st.rerun()

    st.header("Fase 1: Comunicado Interno")
    
    with st.expander("📝 SITUAÇÃO: Informar a equipe sobre o novo Vale Refeição", expanded=True):
        st.write("Sua tarefa é escrever um e-mail curto e profissional informando que o valor do VR aumentou e que o cartão novo chegará em breve.")

    texto_aluno = st.text_area("Digite sua proposta de e-mail interno:", height=200)

    if st.button("Enviar para Revisão"):
        if texto_aluno:
            with st.spinner('O Diretor está analisando seu texto...'):
                try:
                    prompt = f"Aja como um Diretor de RH. Analise o e-mail abaixo escrito por um aluno de administração. Dê um feedback curto (máximo 3 frases) dizendo se está profissional ou o que melhorar: \n\n {texto_aluno}"
                    response = model.generate_content(prompt)
                    feedback = response.text
                    
                    st.subheader("Feedback do Diretor:")
                    st.info(feedback)
                    
                    # Salva os dados na sua planilha automaticamente
                    salvar_na_planilha(st.session_state.nome, texto_aluno, feedback)
                    st.success("Desafio concluído! Seus dados foram salvos no relatório.")
                    
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
        else:
            st.warning("Escreva seu texto antes de enviar.")

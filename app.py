import streamlit as st
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. CONFIGURAÇÃO DA IA (GEMINI) - CHAVE ATUALIZADA
API_KEY = "AIzaSyBMIsMJ9xfSW7IrJhhKGfq1D61dxsguIF8"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 2. CONFIGURAÇÃO DA PLANILHA (GOOGLE SHEETS)
def salvar_na_planilha(nome, texto_aluno, feedback):
    try:
        # Define os acessos necessários
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Tenta carregar o arquivo de credenciais que você subiu no GitHub
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha pelo nome exato que você criou
        sheet = client.open("Relatório de Comunicação - Curso Técnico").sheet1
        
        # Adiciona a linha com os dados
        sheet.append_row([nome, texto_aluno, feedback])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")
        return False

# 3. INTERFACE DO USUÁRIO (STREAMLIT)
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼")

st.title("💼 Sistema de Treinamento Executivo")

# Lógica de Login (Nome do Aluno)
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
    # Cabeçalho Lateral
    st.sidebar.write(f"👤 **Colaborador:** {st.session_state.nome}")
    if st.sidebar.button("Sair/Trocar Nome"):
        del st.session_state.nome
        st.rerun()

    # Desafio de Comunicação
    st.header("Fase 1: Comunicado Interno")
    
    with st.expander("📝 SITUAÇÃO: Informar a equipe sobre o novo Vale Refeição", expanded=True):
        st.write("""
        **Tarefa:** Escreva um e-mail curto e profissional informando que:
        1. O valor do Vale Refeição aumentou em 10%.
        2. Os novos cartões serão entregues na recepção na próxima sexta-feira.
        """)

    texto_aluno = st.text_area("Digite sua proposta de e-mail abaixo:", height=200, placeholder="Prezados...")

    if st.button("Enviar para Revisão"):
        if texto_aluno:
            with st.spinner('O Diretor de RH está lendo seu e-mail...'):
                try:
                    # Prompt para a IA
                    prompt = f"""
                    Aja como um Diretor de RH exigente, mas didático. 
                    Analise o e-mail de um estagiário de administração: '{texto_aluno}'.
                    Dê um feedback direto (máximo 3 frases) em tom profissional.
                    Diga se a comunicação foi clara e se o tom foi adequado.
                    """
                    
                    response = model.generate_content(prompt)
                    feedback = response.text
                    
                    # Exibe o Feedback na tela
                    st.subheader("Feedback do Diretor:")
                    st.info(feedback)
                    
                    # Tenta salvar na planilha
                    if salvar_na_planilha(st.session_state.nome, texto_aluno, feedback):
                        st.success("✅ Desafio concluído! Sua resposta foi salva no relatório do professor.")
                    
                except Exception as e:
                    st.error(f"Houve um problema na análise da IA: {e}")
        else:
            st.warning("Você precisa escrever algo antes de enviar para o Diretor.")

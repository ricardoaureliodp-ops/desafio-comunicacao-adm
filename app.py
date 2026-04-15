import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. FUNÇÃO DE CONEXÃO (AUTO-DETECT DO SEU MANUAL) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: Chave API não configurada nos Secrets."
    
    # Pergunta quais modelos estão liberados para sua chave [cite: 107-108]
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash"
    
    try:
        res = requests.get(url_list, timeout=10) [cite: 111]
        if res.status_code == 200:
            for m in res.json().get('models', []): [cite: 112]
                if 'generateContent' in m.get('supportedGenerationMethods', []): [cite: 113, 116]
                    modelo_final = m['name'] [cite: 117]
                    if "flash" in m['name']: break
    except: pass

    # Chamada oficial via REST API [cite: 118-120, 122]
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text'] if r.status_code == 200 else f"Erro {r.status_code}"
    except Exception as e: return f"Erro: {str(e)}"

# --- 2. FUNÇÃO PARA SALVAR NA PLANILHA ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        # Substitua pelo nome exato da sua planilha
        sheet = client.open("RESULTADOS - SIMULAÇÃO GESTOR - TRILHAS").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except: return False

# --- 3. INTERFACE E REGRAS DE COMUNICAÇÃO ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

# Puxa a chave dos Secrets [cite: 95]
api_key = st.secrets.get("GEMINI_API_KEY")

# Instrução extra para a IA verificar se o aluno deve refazer
regra_refazer = "AO FINAL DO FEEDBACK: Se a avaliação geral for ruim ou o texto for muito informal, adicione a frase: '⚠️ ATENÇÃO: Seu texto não atingiu o padrão mínimo. Por favor, revise as orientações e tente novamente.'."

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Jogo"): st.session_state.clear(); st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Escolha seu desafio:")
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("SITUAÇÃO: Informe a equipe sobre o aumento de 10% no VR e retirada de cartões na sexta.")
        texto_1 = st.text_area("Redija o e-mail interno:", key="t1", height=150)
        if st.button("Enviar para o Diretor (Desafio 1)"):
            with st.spinner("Analisando..."):
                prompt = f"Diretor Administrativo exigente: Analise o e-mail de {nome}: '{texto_1}'. {regra_refazer}"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Avaliação:")
                st.write(res)
                salvar_resultado(nome, "E-mail Interno", res)

    with tab2:
        st.info("SITUAÇÃO: Informe ao cliente que faturas agora são apenas por PDF.")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", key="t2", height=150)
        if st.button("Enviar para o Diretor (Desafio 2)"):
            with st.spinner("Analisando..."):
                prompt = f"Diretor Administrativo exigente: Analise o e-mail para cliente de {nome}: '{texto_2}'. {regra_refazer}"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Avaliação:")
                st.write(res)
                salvar_resultado(nome, "E-mail Externo", res)
else:
    st.warning("👈 Identifique-se na barra lateral.")

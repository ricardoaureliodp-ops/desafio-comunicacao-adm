import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. FUNÇÃO DE CONEXÃO (AUTO-DETECT CONFORME SEU MANUAL) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não encontrada nos Secrets."

    # Pergunta quais modelos estão liberados para sua chave [cite: 107-108]
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash"
    
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo_final = m['name']
                    if "flash" in m['name']: break
    except: pass

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
        # Abre a sua planilha de resultados [cite: 80]
        sheet = client.open("RESULTADOS - SIMULAÇÃO GESTOR - TRILHAS").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except: return False

# --- 3. INTERFACE E LÓGICA DE REFAZER ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

api_key = st.secrets.get("GEMINI_API_KEY")
instrucao_redo = "AO FINAL: Se a nota for abaixo de 7, encerre obrigatoriamente com: '⚠️ ATENÇÃO: Seu texto não atingiu o padrão mínimo. Revise os pontos acima e envie novamente.'."

with st.sidebar:
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Jogo"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])
    
    with tab1:
        st.info("Cenário: Aumento de 10% no VR. Cartões na sexta na recepção.")
        texto_1 = st.text_area("Redija o e-mail interno:", key="t1")
        if st.button("Enviar Desafio 1"):
            with st.spinner("Analisando..."):
                prompt = f"Diretor exigente: Avalie o e-mail de {nome}: '{texto_1}'. {instrucao_redo}"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Avaliação:")
                st.write(res)
                salvar_resultado(nome, "E-mail Interno", res)

    with tab2:
        st.info("Cenário: Faturas agora apenas por PDF. Peça confirmação de dados.")
        texto_2 = st.text_area("Redija o e-mail externo:", key="t2")
        if st.button("Enviar Desafio 2"):
            with st.spinner("Analisando..."):
                prompt = f"Diretor exigente: Avalie o e-mail para cliente de {nome}: '{texto_2}'. {instrucao_redo}"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Avaliação:")
                st.write(res)
                salvar_resultado(nome, "E-mail Externo", res)
else:
    st.warning("👈 Identifique-se na lateral.")

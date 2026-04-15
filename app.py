import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- FUNÇÃO DE CONEXÃO (AUTO-DETECT DO SEU MANUAL) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não encontrada."
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
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "O Diretor está ocupado. Tente novamente."

# --- FUNÇÃO PARA SALVAR NA PLANILHA ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("RESULTADOS - SIMULAÇÃO GESTOR - TRILHAS").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except: return False

# --- INTERFACE ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Simulador"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])
    regra_redo = "IMPORTANTE: Se a nota for abaixo de 7 ou o texto for inadequado, termine com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."

    with tab1:
        st.info("Cenário: VR aumentou 10%. Cartões sexta na recepção.")
        texto_1 = st.text_area("Redija o e-mail interno:", key="t1")
        if st.button("Enviar Desafio 1"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"Diretor exigente: Avalie o e-mail de {nome}: '{texto_1}'. {regra_redo}", api_key)
                st.write(res)
                salvar_resultado(nome, "E-mail Interno", res)

    with tab2:
        st.info("Cenário: Faturas agora apenas por PDF. Peça confirmação.")
        texto_2 = st.text_area("Redija o e-mail externo:", key="t2")
        if st.button("Enviar Desafio 2"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"Diretor exigente: Avalie o e-mail externo de {nome}: '{texto_2}'. {regra_redo}", api_key)
                st.write(res)
                salvar_resultado(nome, "E-mail Externo", res)
else:
    st.warning("Identifique-se na lateral.")

import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO IA (SEM SUGESTÕES NO FEEDBACK) ---
def chamar_gemini(prompt, api_key):
    if not api_key: return "Erro: Chave não configurada."
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo = "models/gemini-1.5-flash"
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo = m['name']; break
    except: pass
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "O Diretor está ocupado. Tente novamente."

# --- 2. SALVAR NA PLANILHA (Ajuste de Assinatura JWT) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        with open('credentials.json') as f:
            info = json.load(f)
        
        # Limpeza profunda da chave para evitar o erro de Assinatura Inválida
        key = info['private_key']
        if "\\n" in key:
            info['private_key'] = key.replace("\\n", "\n")
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Erro no salvamento: {e}")
        return False

# --- 3. INTERFACE E REGRAS ---
st.set_page_config(page_title="Simulador Jovem Aprendiz", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# Comando para a IA APENAS CRITICAR, sem dar sugestão de texto pronto
comando_ia = (
    "Aja como um Diretor Administrativo rigoroso. Avalie o e-mail enviado pelo aprendiz. "
    "APONTE APENAS OS ERROS DE PORTUGUÊS, TOM E ETIQUETA PROFISSIONAL. "
    "NÃO DÊ SUGESTÕES DE TEXTO PRONTO E NÃO ESCREVA UMA 'VERSÃO IDEAL'. "
    "Foque exclusivamente em mostrar onde o aluno errou e por que o tom está inadequado. "
    "Se a nota for baixa, termine com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'"
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome Completo:")
    if st.button("Reiniciar"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 E-mail Interno (VR)", "🤝 E-mail Externo (PDF)"])

    with tab1:
        st.markdown("**Missão 1:** Avise a equipe que o VR (Vale Refeição) aumentou 10%. Retirada dos cartões na Recepção apenas nesta sexta.")
        texto_1 = st.text_area("Digite o e-mail interno:", key="t1", height=150)
        if st.button("Enviar para o Diretor (1)"):
            with st.spinner("Analisando..."):
                prompt = f"{comando_ia}\n\nE-mail de {nome}: '{texto_1}'"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.markdown("**Missão 2:** Avise ao cliente que faturas agora são apenas por PDF por e-mail. Peça confirmação de dados.")
        texto_2 = st.text_area("Digite o e-mail externo:", key="t2", height=150)
        if st.button("Enviar para o Diretor (2)"):
            with st.spinner("Analisando..."):
                prompt = f"{comando_ia}\n\nE-mail de {nome}: '{texto_2}'"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Identifique-se ao lado.")

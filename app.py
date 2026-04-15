import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO COM A IA (SÓ CRÍTICA, SEM DAR A RESPOSTA) ---
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
    except: return "O Diretor está ocupado. Tente de novo."

# --- 2. SALVAR NA PLANILHA (LIMPEZA TOTAL DE CHAVE) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo o arquivo e forçando a limpeza da chave privada
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # Correção definitiva para o erro de assinatura (JWT Signature)
        if 'private_key' in creds_data:
            creds_data['private_key'] = creds_data['private_key'].replace('\\n', '\n')
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha exata
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Se der erro, ele aparece na lateral
        st.sidebar.error(f"Erro de Gravação: {str(e)}")
        return False

# --- 3. INTERFACE E REGRAS DO DIRETOR ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# PROMPT: SÓ CRÍTICAS, NADA DE DAR O PEIXE
regra_diretor = (
    "Aja como um Diretor Administrativo extremamente rígido. "
    "Sua única tarefa é CRITICAR e APONTAR OS ERROS do e-mail do aprendiz. "
    "REGRAS ABSOLUTAS: "
    "1. NÃO dê sugestões de texto. "
    "2. NÃO escreva 'versão ideal' ou 'como deveria ser'. "
    "3. NÃO dê exemplos de frases corretas. "
    "4. Apenas diga o que está errado (português, tom, falta de educação, clareza). "
    "No final, dê uma nota de 0 a 10. Se a nota for menor que 7, escreva: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Limpar e Reiniciar"): 
        st.session_state.clear()
        st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 E-mail Interno (VR)", "🤝 E-mail Externo (PDF)"])

    with tab1:
        st.info("SITUAÇÃO: O VR aumentou 10%. Cartões na Recepção nesta sexta.")
        texto_1 = st.text_area("Redija o e-mail interno:", key="t1", height=150)
        if st.button("Enviar para Crítica (1)"):
            with st.spinner("O Diretor está lendo..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.info("SITUAÇÃO: Faturas apenas por PDF no e-mail. Peça confirmação.")
        texto_2 = st.text_area("Redija o e-mail externo:", key="t2", height=150)
        if st.button("Enviar para Crítica (2)"):
            with st.spinner("O Diretor está analisando..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Digite seu nome na lateral.")

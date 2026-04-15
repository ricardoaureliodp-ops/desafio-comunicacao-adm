import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. IA: CHAMADA ROBUSTA ---
def chamar_gemini(prompt, api_key):
    if not api_key: return "Erro: Chave API não configurada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na IA ({r.status_code}): {r.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- 2. GRAVAÇÃO: MÉTODO GARANTIDO ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Puxa direto das secrets
        creds_dict = dict(st.secrets["gspread_creds"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Erro de Gravação: {str(e)}")
        return False

# --- 3. INTERFACE ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

instrucao_diretor = (
    "Aja como um Diretor Administrativo rigoroso. Analise o e-mail do aprendiz. "
    "1. Se houver CAIXA ALTA, critique duramente dizendo que equivale a GRITAR. "
    "2. Critique gírias e informalidade. 3. NÃO DÊ O TEXTO PRONTO. "
    "Dê nota de 0 a 10. Se nota < 7, diga: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Reiniciar"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 Missão 1: Interno", "🤝 Missão 2: Externo"])
    with tab1:
        st.markdown("**SITUAÇÃO:** VR aumentou 10%. Cartões na Recepção nesta sexta.")
        texto_1 = st.text_area("Digite o e-mail interno:", key="t1", height=150)
        if st.button("Enviar para o Diretor (1)"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"{instrucao_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)
    with tab2:
        st.markdown("**SITUAÇÃO:** Faturas por PDF. Peça confirmação de dados.")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", key="t2", height=150)
        if st.button("Enviar para o Diretor (2)"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"{instrucao_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Identifique-se na lateral.")

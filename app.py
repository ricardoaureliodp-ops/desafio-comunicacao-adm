import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. IA: CRÍTICA RIGOROSA (SEM DAR RESPOSTA) ---
def chamar_gemini(prompt, api_key):
    if not api_key: return "Erro: Chave não configurada."
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "O Diretor está ocupado. Tente novamente."

# --- 2. GRAVAÇÃO: MÉTODO GARANTIDO VIA SECRETS ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lê direto das Secrets que você acabou de salvar
        creds_dict = dict(st.secrets["gspread_creds"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # Nome exato da sua planilha
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar: {str(e)}")
        return False

# --- 3. INTERFACE ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

comando_diretor = (
    "Aja como um Diretor Administrativo implacável. Analise o e-mail do Jovem Aprendiz. "
    "REGRAS: 1. Se usar CAIXA ALTA, diga que é agressivo e equivale a GRITAR. "
    "2. Critique gírias ('lindos', 'pega aí') e informalidade. 3. NÃO DÊ O TEXTO PRONTO. "
    "Dê uma nota final. Se < 7, diga: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    nome = st.text_input("Nome Completo:")
    if st.button("Reiniciar"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 Missão 1: Interno", "🤝 Missão 2: Externo"])
    with tab1:
        st.markdown("**SITUAÇÃO:** VR aumentou 10%. Cartões na Recepção nesta sexta.")
        texto_1 = st.text_area("Digite o e-mail interno:", key="t1", height=150)
        if st.button("Enviar para o Diretor (1)"):
            res = chamar_gemini(f"{comando_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
            st.write(res)
            salvar_resultado(nome, "Interno (VR)", res)
    with tab2:
        st.markdown("**SITUAÇÃO:** Faturas por PDF. Peça confirmação de dados.")
        texto_2 = st.text_area("Digite o e-mail externo:", key="t2", height=150)
        if st.button("Enviar para o Diretor (2)"):
            res = chamar_gemini(f"{comando_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
            st.write(res)
            salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Identifique-se na lateral.")

import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- FUNÇÃO DA IA ---
def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=20)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Erro ao conectar com o Diretor. Verifique a GEMINI_API_KEY nas Secrets."

# --- FUNÇÃO DA PLANILHA ---
def salvar_resultado(nome, atividade, feedback):
    try:
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["PROJECT_ID"],
            "private_key": st.secrets["PRIVATE_KEY"],
            "client_email": st.secrets["CLIENT_EMAIL"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar: {str(e)}")
        return False

# --- INTERFACE ---
st.set_page_config(page_title="Simulador", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

with st.sidebar:
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Limpar Tudo"): st.session_state.clear(); st.rerun()

if nome:
    prompt_diretor = (
        "Aja como um Diretor Administrativo rigoroso. Critique o e-mail do aprendiz de forma pedagógica. "
        "Se houver CAIXA ALTA, diga que ele está gritando e isso é inaceitável. Critique gírias. "
        "NÃO dê o texto pronto. Dê uma nota de 0 a 10. Se nota < 7, escreva: '⚠️ REFAÇA O E-MAIL.'"
    )

    tab1, tab2 = st.tabs(["📧 Missão 1", "🤝 Missão 2"])

    with tab1:
        st.subheader("Cenário: VR aumentou 10%. Avisar equipe.")
        texto1 = st.text_area("Seu e-mail interno:", key="t1")
        if st.button("Enviar para o Diretor (1)"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"{prompt_diretor}\n\nE-mail: {texto1}")
                st.write(res)
                salvar_resultado(nome, "Interno", res)

    with tab2:
        st.subheader("Cenário: Faturas por PDF. Avisar cliente.")
        texto2 = st.text_area("Seu e-mail externo:", key="t2")
        if st.button("Enviar para o Diretor (2)"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"{prompt_diretor}\n\nE-mail: {texto2}")
                st.write(res)
                salvar_resultado(nome, "Externo", res)
else:
    st.warning("👈 Digite seu nome ao lado para começar.")

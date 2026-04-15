import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CHAMADA DA IA (DIRETOR EXPLICATIVO E RÍGIDO) ---
def chamar_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na API: Verifique se a GEMINI_API_KEY está correta nas Secrets. (Erro {r.status_code})"
    except:
        return "Erro de conexão com o Diretor."

# --- 2. GRAVAÇÃO NA PLANILHA (MÉTODO BLINDADO) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lê o JSON inteiro direto da Secret
        creds_info = json.loads(st.secrets["GOOGLE_JSON"])
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
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
    "Aja como um Diretor Administrativo rigoroso e detalhista. "
    "Sua tarefa é fazer uma CRÍTICA PEDAGÓGICA E LONGA do e-mail de um Jovem Aprendiz. "
    "REGRAS OBRIGATÓRIAS: "
    "1. ANALISE TUDO: Se o aluno usar CAIXA ALTA, explique longamente por que isso é falta de respeito e etiqueta. "
    "2. Critique gírias ('LINDOS', 'VIU', 'PEGA AÍ') e a falta de formalidade. "
    "3. EXIJA saudação profissional e despedida. "
    "4. NÃO DÊ O TEXTO PRONTO. O aluno deve sofrer para descobrir a solução sozinho. "
    "5. Explique o IMPACTO que um e-mail ruim tem na imagem da empresa. "
    "No final, dê uma nota de 0 a 10. Se nota < 7, termine com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Reiniciar"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 Missão 1: Interno (VR)", "🤝 Missão 2: Externo (PDF)"])
    
    with tab1:
        st.info("SITUAÇÃO: VR aumentou 10%. Retirada dos cartões na Recepção apenas nesta sexta.")
        texto_1 = st.text_area("Redija o e-mail interno:", key="t1", height=200)
        if st.button("Enviar para Avaliação (1)"):
            with st.spinner("O Diretor está analisando..."):
                res = chamar_gemini(f"{comando_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.info("SITUAÇÃO: Faturas agora são apenas por PDF. Informe o cliente e peça confirmação.")
        texto_2 = st.text_area("Redija o e-mail externo:", key="t2", height=200)
        if st.button("Enviar para Avaliação (2)"):
            with st.spinner("Analisando..."):
                res = chamar_gemini(f"{comando_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Identifique-se na lateral para começar.")

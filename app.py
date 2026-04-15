import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO IA (FEEDBACK RIGOROSO E EXPLICATIVO) ---
def chamar_gemini(prompt, api_key):
    if not api_key: return "Erro: Chave API não configurada."
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "O Diretor está em reunião. Tente novamente em instantes."

# --- 2. GRAVAÇÃO NA PLANILHA (VIA SECRETS) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gspread_creds"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Aviso de Gravação: {str(e)}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

comando_diretor = (
    "Aja como um Diretor Administrativo experiente e muito exigente. "
    "Sua função é avaliar o e-mail de um Jovem Aprendiz de forma pedagógica, mas firme. "
    "REGRAS CRÍTICAS: "
    "1. Se o aluno usar CAIXA ALTA, explique que isso é falta de etiqueta e equivale a GRITAR. "
    "2. Critique o uso de gírias e tratamentos informais (como 'LINDOS' ou 'VIU'). "
    "3. APONTE OS ERROS de pontuação e falta de profissionalismo. "
    "4. PROIBIÇÃO: Não dê sugestões de texto pronto. O aluno deve descobrir como corrigir sozinho. "
    "5. Dê uma nota de 0 a 10. Se a nota for menor que 7, termine com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Limpar e Reiniciar"): 
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Realize as missões com atenção máxima:")
    tab1, tab2 = st.tabs(["📧 Missão 1: Interno (VR)", "🤝 Missão 2: Externo (PDF)"])

    with tab1:
        st.markdown("""
        **Contexto:** O VR (Vale Refeição) é o benefício para alimentação. A empresa aumentou o valor em **10%**.
        
        **Sua Tarefa:** Escreva um e-mail para todos os colaboradores informando que:
        * O valor subiu **10%**.
        * Os novos cartões devem ser retirados na **Recepção**.
        * A retirada é obrigatória apenas nesta **sexta-feira**.
        
        *Lembre-se: Use linguagem formal, saudação e despedida. Não grite!*
        """)
        texto_1 = st.text_area("Redija o e-mail interno:", key="t1", height=200)
        if st.button("Enviar para Avaliação (1)"):
            with st.spinner("O Diretor está analisando..."):
                res = chamar_gemini(f"{comando_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.markdown("""
        **Contexto:** Modernização Digital. Não enviaremos mais faturas de papel para os clientes.
        
        **Sua Tarefa:** Escreva para um cliente informando que:
        * A partir do próximo mês, as faturas serão enviadas **apenas por E-mail (PDF)**.
        * Peça para o cliente **confirmar** se o e-mail dele está correto no sistema.
        
        *Lembre-se: O cliente é a prioridade. Seja extremamente educado e cordial.*
        """)
        texto_2 = st.text_area("Redija o e-mail para o cliente:", key="t2", height=200)
        if st.button("Enviar para Avaliação (2)"):
            with st.spinner("Analisando atendimento..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Identifique-se na lateral para começar.")

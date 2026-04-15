import streamlit as st
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO IA (Lógica Anti-Erro do seu Manual) ---
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
    except: return "O Diretor está ocupado agora. Tente novamente."

# --- 2. SALVAR NA PLANILHA NOVA ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        # NOME DA NOVA PLANILHA LIMPA QUE VOCÊ CRIOU
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar na planilha: {e}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES DETALHADAS ---
st.set_page_config(page_title="Simulador Jovem Aprendiz", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")
regra_redo = "⚠️ Se a nota for baixa ou o tom inadequado, termine obrigatoriamente com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Reiniciar Simulador"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 E-mail Interno (Equipe)", "🤝 E-mail Externo (Cliente)"])

    with tab1:
        st.markdown("""
        ### Missão 1: Comunicado de Benefício (VR)
        **O que é VR?** Significa **Vale Refeição**. É um valor em dinheiro que a empresa carrega em um cartão para você pagar o seu almoço.
        
        **Cenário:** O valor do VR da empresa aumentou em **10%**!
        **Sua Tarefa:** Escreva um e-mail para todos os seus colegas avisando sobre essa novidade.
        **Dados que não podem faltar:** 1. O aumento é de **10%**.
        2. Os novos cartões devem ser retirados na **Recepção**.
        3. A retirada deve ser feita **somente nesta sexta-feira**.
        
        *Dica: Seja profissional. Use saudações como 'Prezados Colaboradores' ou 'Equipe'.*
        """)
        texto_1 = st.text_area("Redija o e-mail interno aqui:", key="t1", height=200)
        if st.button("Enviar para o Diretor (Missão 1)"):
            with st.spinner("Analisando sua escrita..."):
                res = chamar_gemini(f"Avalie como Diretor o e-mail de {nome}: '{texto_1}'. {regra_redo}", api_key)
                st.subheader("📋 Avaliação do Diretor:")
                st.write(res)
                salvar_resultado(nome, "E-mail Interno (VR)", res)

    with tab2:
        st.markdown("""
        ### Missão 2: Modernização e Boletos em PDF
        **O que está acontecendo?** A empresa quer ser sustentável e rápida. Não enviaremos mais papéis pelo correio.
        
        **Tarefa:** Escreva para um cliente informando que, a partir do próximo mês, as contas serão enviadas apenas por **E-mail em formato PDF**.
        **Dados que não podem faltar:**
        1. A mudança começa no **próximo mês**.
        2. O envio agora é digital (PDF).
        3. Peça para o cliente **confirmar** se o e-mail de cadastro dele está atualizado.
        
        *Dica: Seja muito cordial e educado, pois ele é um cliente!*
        """)
        texto_2 = st.text_area("Redija o e-mail para o cliente aqui:", key="t2", height=200)
        if st.button("Enviar para o Diretor (Missão 2)"):
            with st.spinner("Analisando seu atendimento..."):
                res = chamar_gemini(f"Avalie como Diretor o e-mail externo de {nome}: '{texto_2}'. {regra_redo}", api_key)
                st.subheader("📋 Avaliação do Diretor:")
                st.write(res)
                salvar_resultado(nome, "E-mail Externo (PDF)", res)
else:
    st.warning("👈 Digite seu nome completo na barra lateral para começar.")

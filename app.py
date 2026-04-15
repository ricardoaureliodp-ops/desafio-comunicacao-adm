import streamlit as st
import requests

# --- 1. FUNÇÃO DE CONEXÃO (BASEADA NO SEU PDF) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."

    # 1. Pergunta ao Google quais modelos sua chave pode usar
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash" 
    
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            modelos_disponiveis = res.json().get('models', [])
            for m in modelos_disponiveis:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo_final = m['name']
                    if "flash" in m['name']:
                        break
    except:
        pass 

    # 2. Faz a chamada oficial
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"O Diretor está ocupado (Erro {r.status_code})."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- 2. INTERFACE PEDAGÓGICA ---
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Jogo"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Escolha seu desafio de hoje:")
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("SITUAÇÃO: Aviso de Benefício. Informe a equipe que o VR aumentou 10% e os cartões chegam sexta na recepção.")
        texto_1 = st.text_area("Redija seu e-mail aqui:", height=180, key="t1")
        if st.button("Enviar para o Diretor (Desafio 1)"):
            with st.spinner("Analisando..."):
                prompt = f"Diretor exigente: Avalie o e-mail de {nome}: {texto_1}. Feedback detalhado em Português e Administração."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))

    with tab2:
        st.info("SITUAÇÃO: Digitalização. Informe ao cliente que faturas agora são apenas por E-mail (PDF).")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", height=180, key="t2")
        if st.button("Enviar para o Diretor (Desafio 2)"):
            with st.spinner("Analisando..."):
                prompt = f"Avalie o e-mail de {nome} para um cliente: {texto_2}."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))
else:
    st.warning("Identifique-se na lateral para começar.")

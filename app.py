import streamlit as st
import requests

# --- 1. FUNÇÃO DE CONEXÃO (BASEADA NO SEU MANUAL TÉCNICO) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."

    # 1. Pergunta ao Google quais modelos sua chave pode usar 
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash" # Padrão de segurança
    
    try:
        res = requests.get(url_list, timeout=10) [cite: 111]
        if res.status_code == 200:
            for m in res.json().get('models', []): [cite: 112]
                if 'generateContent' in m.get('supportedGenerationMethods', []): [cite: 113, 116]
                    modelo_final = m['name'] [cite: 114, 117]
                    if "flash" in m['name']:
                        break
    except:
        pass 

    # 2. Faz a chamada oficial para o endereço liberado [cite: 118, 119, 120]
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]} [cite: 121]
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15) [cite: 122]
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text'] [cite: 123]
        else:
            return f"O Diretor está analisando outros casos (Erro {r.status_code}). Tente novamente."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- 2. INTERFACE PEDAGÓGICA ---
st.set_page_config(page_title="Simulador Administrativo", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

# Puxa a chave dos Secrets de forma segura [cite: 95]
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar: [cite: 38]
    st.header("👤 Identificação") [cite: 39]
    nome = st.text_input("Nome do Aprendiz:") [cite: 40]
    if st.button("Reiniciar Jogo"): [cite: 42]
        st.session_state.clear() [cite: 43]
        st.rerun() [cite: 44]

if nome:
    st.write(f"### Olá, {nome}! Escolha seu desafio de hoje:")
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("**SITUAÇÃO:** Aviso de Benefício. Informe a equipe que o VR aumentou 10% e os cartões chegam sexta na recepção.")
        texto_1 = st.text_area("Redija seu e-mail aqui:", height=180, key="t1")
        if st.button("Enviar para o Diretor (Desafio 1)"):
            with st.spinner("Analisando sua escrita..."):
                prompt = f"Diretor Administrativo exigente: Analise o e-mail de {nome}: '{texto_1}'. Feedback detalhado: 1. Erros de Português. 2. Conceitos Administrativos e Tom. 3. Versão Ideal."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))

    with tab2:
        st.info("**SITUAÇÃO:** Digitalização. Informe ao cliente que faturas agora são apenas por PDF e peça confirmação dos dados.")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", height=180, key="t2")
        if st.button("Enviar para o Diretor (Desafio 2)"):
            with st.spinner("O Diretor está avaliando..."):
                prompt = f"Diretor Administrativo: Analise o português e o tom administrativo deste e-mail de {nome} para um cliente: '{texto_2}'."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))
else:
    st.warning("👈 Identifique-se na barra lateral para começar a aula.")

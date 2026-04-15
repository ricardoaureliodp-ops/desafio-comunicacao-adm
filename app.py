import streamlit as st
import requests

# --- 1. FUNÇÃO DE CONEXÃO (COM TIMEOUT AMPLIADO) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."

    # 1. Auto-Detect do Modelo conforme seu Manual [cite: 107-114]
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash" 
    
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo_final = m['name']
                    if "flash" in m['name']:
                        break
    except:
        pass 

    # 2. Chamada com Timeout de 30 segundos 
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # Aumentamos para 30 segundos para o Diretor ter tempo de pensar
        r = requests.post(url_chat, json=payload, timeout=30) 
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"O Diretor teve um imprevisto (Erro {r.status_code}). Tente enviar de novo."
    except Exception as e:
        return f"O sinal falhou: {str(e)}. Tente novamente em instantes."

# --- 2. INTERFACE DO SIMULADOR ---
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Simulador"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Bem-vindo, {nome}! Escolha sua missão:")
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("**SITUAÇÃO:** Aviso de Benefício. Informe o aumento de 10% no VR e cartões na sexta.")
        texto_1 = st.text_area("Redija o e-mail interno:", height=180, key="t1")
        if st.button("Enviar para Avaliação (Desafio 1)"):
            with st.spinner("O Diretor está analisando detalhadamente..."):
                prompt = f"Diretor Administrativo: Avalie o e-mail de {nome}: '{texto_1}'. Feedback detalhado: 1. Português. 2. Conceitos e Tom. 3. Versão Ideal."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))

    with tab2:
        st.info("**SITUAÇÃO:** Digitalização. Informe ao cliente que faturas agora são apenas por PDF.")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", height=180, key="t2")
        if st.button("Enviar para Avaliação (Desafio 2)"):
            with st.spinner("Analisando atendimento..."):
                prompt = f"Avalie o português e o tom administrativo deste e-mail de {nome} para cliente: '{texto_2}'."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))
else:
    st.warning("👈 Identifique-se na barra lateral para começar a aula.")

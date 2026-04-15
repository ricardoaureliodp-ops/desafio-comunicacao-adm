import streamlit as st
import requests

# --- 1. FUNÇÃO DE CONEXÃO (MÉTODO REST API DO SEU MANUAL) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."

    # Tenta primeiro o modelo Flash, que é o mais rápido e atualizado
    modelo = "models/gemini-1.5-flash"
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # Se o Flash falhar, tenta o modelo Pro como alternativa automática
            url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            r_alt = requests.post(url_alt, json=payload, timeout=15)
            if r_alt.status_code == 200:
                return r_alt.json()['candidates'][0]['content']['parts'][0]['text']
            return f"O Diretor está ocupado agora (Erro {r.status_code})."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- 2. INTERFACE DO SIMULADOR ---
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

# Puxa a chave dos Secrets de forma segura [cite: 95]
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
        st.info("**SITUAÇÃO:** Aviso de Benefício. Informe a equipe que o VR aumentou 10% e os cartões chegam sexta na recepção.")
        texto_1 = st.text_area("Redija seu e-mail interno aqui:", height=180, key="t1")
        if st.button("Enviar para o Diretor (Desafio 1)"):
            if texto_1:
                with st.spinner("Analisando sua escrita..."):
                    prompt = f"Aja como um Diretor Administrativo rigoroso. Avalie o e-mail de {nome}: '{texto_1}'. Dê feedback detalhado sobre Português e conceitos de comunicação empresarial."
                    st.subheader("📋 Avaliação do Diretor:")
                    st.write(chamar_gemini(prompt, api_key))
            else:
                st.warning("Escreva o texto antes de enviar.")

    with tab2:
        st.info("**SITUAÇÃO:** Digitalização. Informe ao cliente que faturas agora são apenas por PDF e peça confirmação dos dados.")
        texto_2 = st.text_area("Redija seu e-mail para o cliente:", height=180, key="t2")
        if st.button("Enviar para o Diretor (Desafio 2)"):
            if texto_2:
                with st.spinner("O Diretor está analisando..."):
                    prompt = f"Avalie o português e o tom administrativo deste e-mail para um cliente: '{texto_2}'. Feedback para o aluno {nome}."
                    st.subheader("📋 Avaliação do Diretor:")
                    st.write(chamar_gemini(prompt, api_key))
            else:
                st.warning("Escreva o texto antes de enviar.")
else:
    st.warning("👈 Identifique-se na barra lateral para começar a aula.")

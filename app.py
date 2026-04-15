import streamlit as st
import requests

# --- 1. FUNÇÃO DE CONEXÃO (BASEADA NO SEU PDF) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."
    
    # Endpoint estável v1beta conforme seu guia [cite: 119]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # Se der erro 404, tentamos sem o prefixo 'models/' automaticamente
            url_alt = f"https://generativelanguage.googleapis.com/v1beta/gemini-1.5-flash:generateContent?key={api_key}"
            r2 = requests.post(url_alt, json=payload, timeout=15)
            if r2.status_code == 200:
                return r2.json()['candidates'][0]['content']['parts'][0]['text']
            return f"Erro {r.status_code}: {r.text}"
    except Exception as e:
        return f"Erro de rede: {str(e)}"

# --- 2. INTERFACE COM AS INSTRUÇÕES QUE VOCÊ GOSTOU ---
st.set_page_config(page_title="Treinamento Administrativo", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Jogo"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Selecione seu desafio abaixo:")
    
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("""
        **SITUAÇÃO:** Aviso de Benefício.
        **Tarefa:** Informe a equipe que o Vale Refeição aumentou 10% e os cartões novos chegam sexta na recepção.
        **O que o Diretor avaliará:** Português, clareza e tom profissional.
        """)
        texto_1 = st.text_area("Redija o e-mail interno:", height=150, key="t1")
        if st.button("Enviar para o Diretor", key="b1"):
            with st.spinner("Analisando..."):
                prompt = f"Aja como um Diretor de RH. Avalie o e-mail de {nome}: {texto_1}. Dê feedback detalhado sobre Português e Conceitos Administrativos."
                st.write(chamar_gemini(prompt, api_key))

    with tab2:
        st.info("""
        **SITUAÇÃO:** Mudança de Processo (Digitalização).
        **Tarefa:** Informe ao cliente que faturas agora são apenas por E-mail (PDF) e peça confirmação dos dados.
        **O que o Diretor avaliará:** Cordialidade e precisão das informações.
        """)
        texto_2 = st.text_area("Redija o e-mail externo:", height=150, key="t2")
        if st.button("Enviar para o Diretor", key="b2"):
            with st.spinner("Analisando..."):
                prompt = f"Aja como um Diretor Administrativo. Avalie o e-mail de {nome} para um cliente: {texto_2}. Analise Português, Tom de voz e se a informação do PDF ficou clara."
                st.write(chamar_gemini(prompt, api_key))
else:
    st.warning("Identifique-se na lateral para começar.")

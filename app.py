import streamlit as st
import requests

# --- 1. FUNÇÃO DE CONEXÃO (AUTO-DETECT DO SEU MANUAL) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não encontrada nos Secrets."

    # 1. Pergunta quais modelos estão liberados para sua chave [cite: 108]
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash" # Padrão de segurança
    
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                # Verifica se o modelo aceita gerar conteúdo [cite: 113, 116]
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo_final = m['name'] # Pega o nome exato [cite: 117]
                    if "flash" in m['name']:
                        break
    except:
        pass

    # 2. Faz a chamada oficial para o endereço detectado [cite: 119-120]
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"O Diretor está ocupado (Erro {r.status_code}). Verifique o faturamento."
    except Exception as e:
        return f"Erro de rede: {str(e)}"

# --- 2. INTERFACE COM OS DESAFIOS DETALHADOS ---
st.set_page_config(page_title="Treinamento Executivo", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

# Puxa a chave dos Secrets [cite: 95]
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Simulador"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Bem-vindo, {nome}! Escolha sua tarefa:")
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("**SITUAÇÃO:** Aviso de Benefício. Informe a equipe que o VR aumentou 10% e os cartões novos chegam sexta na recepção.")
        texto_1 = st.text_area("Redija o e-mail interno:", height=150, key="t1")
        if st.button("Enviar para Avaliação (Desafio 1)"):
            with st.spinner("O Diretor está analisando..."):
                prompt = f"Aja como Diretor de RH. Avalie o e-mail de {nome}: '{texto_1}'. Feedback detalhado: 1. Português (gramática/ortografia). 2. Conceitos (tom e informações). 3. Versão Ideal."
                st.subheader("📋 Feedback do Diretor:")
                st.write(chamar_gemini(prompt, api_key))

    with tab2:
        st.info("**SITUAÇÃO:** Digitalização. Informe ao cliente que faturas agora são apenas por PDF.")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", height=150, key="t2")
        if st.button("Enviar para Avaliação (Desafio 2)"):
            with st.spinner("Analisando..."):
                prompt = f"Avalie o português e o tom administrativo deste e-mail para cliente: '{texto_2}'. Feedback para o aluno {nome}."
                st.subheader("📋 Feedback do Diretor:")
                st.write(chamar_gemini(prompt, api_key))
else:
    st.warning("👈 Identifique-se na lateral para começar.")

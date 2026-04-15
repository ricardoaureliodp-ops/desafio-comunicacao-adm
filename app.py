import streamlit as st
import requests

# FUNÇÃO DE CHAMADA DIRETA (ANTI-ERRO 400)
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: Chave API não encontrada nos Secrets."

    # Forçamos o modelo mais estável e atualizado
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # Se der erro, ele vai te mostrar o motivo real escrito pelo Google
            return f"Erro {r.status_code}: {r.text}"
    except Exception as e:
        return f"Erro de rede: {str(e)}"

# INTERFACE
st.title("💼 Simulador de Comunicação")
api_key = st.secrets.get("GEMINI_API_KEY")
nome = st.sidebar.text_input("Seu Nome:")

if nome:
    st.write(f"Olá {nome}, redija o e-mail abaixo:")
    texto = st.text_area("Corpo do e-mail:")
    if st.button("Avaliar"):
        with st.spinner("Analisando..."):
            feedback = chamar_gemini(f"Avalie o português e o tom administrativo deste e-mail: {texto}", api_key)
            st.info(feedback)
else:
    st.warning("Digite seu nome na lateral.")

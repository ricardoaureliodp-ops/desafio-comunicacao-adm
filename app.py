import streamlit as st
import requests
from datetime import datetime

# --- FUNÇÃO GEMINI ---
def chamar_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Erro ao gerar resposta."

# --- FUNÇÃO SALVAR PLANILHA ---
def salvar(dados, url):
    try:
        requests.post(url, json=dados)
    except:
        pass

# --- CONFIG ---
st.set_page_config(page_title="Simulador de Comunicação", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

api_key = st.secrets["GEMINI_API_KEY"]
webhook = st.secrets["SHEETS_WEBHOOK_URL"]

# --- IDENTIFICAÇÃO ---
nome = st.text_input("Digite seu nome:")

if "tentativa" not in st.session_state:
    st.session_state.tentativa = 1

# --- JOGO ---
if nome:
    st.write("### Missão: Comunicação Interna")

    texto = st.text_area("Escreva o e-mail:")

    if st.button("Enviar"):
        if texto.strip() == "":
            st.warning("Digite algo.")
        else:
            prompt = f"""
Você é um avaliador de comunicação empresarial.

Analise o texto abaixo.

Responda assim:
Acertou em:
- ...

Precisa melhorar em:
- ...

Avaliação geral:
- ...

Regras:
- Seja direto
- Não reescreva o texto
- Não dê modelo pronto

Texto:
{texto}
"""

            feedback = chamar_gemini(prompt, api_key)

            st.subheader("📋 Feedback")
            st.write(feedback)

            status = "Aceito"
            if "melhorar" in feedback.lower():
                status = "Precisa melhorar"

            dados = {
                "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "nome": nome,
                "tema": "Comunicação",
                "missao": "Email Interno",
                "tentativa": st.session_state.tentativa,
                "resposta_aluno": texto,
                "feedback_ia": feedback,
                "status": status
            }

            salvar(dados, webhook)

            st.session_state.tentativa += 1
else:
    st.info("Digite seu nome para começar.")

import streamlit as st
import requests
from datetime import datetime

# --- 1. FUNÇÃO GEMINI COM AUTO-DETECT DO MODELO ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: GEMINI_API_KEY não configurada nos Secrets."

    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash"

    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    modelo_final = m["name"]
                    if "flash" in m["name"]:
                        break
    except:
        pass

    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"O Diretor teve um imprevisto. Erro {r.status_code}: {r.text}"
    except Exception as e:
        return f"O sinal falhou: {str(e)}"


# --- 2. FUNÇÃO PARA SALVAR NA PLANILHA ---
def salvar_planilha(dados, webhook_url):
    if not webhook_url:
        return False, "Erro: SHEETS_WEBHOOK_URL não configurada nos Secrets."

    try:
        resposta = requests.post(webhook_url, json=dados, timeout=20)

        if resposta.status_code == 200:
            return True, "Resposta salva na planilha."
        else:
            return False, f"Erro ao salvar. Status {resposta.status_code}: {resposta.text}"

    except Exception as e:
        return False, f"Erro de conexão com a planilha: {str(e)}"


# --- 3. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Comunicação",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Simulador de Comunicação Empresarial")

api_key = st.secrets.get("GEMINI_API_KEY")
webhook_url = st.secrets.get("SHEETS_WEBHOOK_URL")


# --- 4. IDENTIFICAÇÃO ---
with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")

    if st.button("Reiniciar Simulador"):
        st.session_state.clear()
        st.rerun()


if "tentativa_1" not in st.session_state:
    st.session_state.tentativa_1 = 1

if "tentativa_2" not in st.session_state:
    st.session_state.tentativa_2 = 1


# --- 5. JOGO ---
if nome:
    st.write(f"### Bem-vindo, {nome}! Escolha sua missão:")

    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("**SITUAÇÃO:** Aviso de Benefício. Informe o aumento de 10% no VR e que os cartões serão carregados na sexta-feira.")

        texto_1 = st.text_area("Redija o e-mail interno:", height=180, key="t1")

        if st.button("Enviar para Avaliação (Desafio 1)"):
            if not texto_1.strip():
                st.warning("Digite o texto antes de enviar.")
            else:
                with st.spinner("O Diretor está analisando..."):

                    prompt = f"""
Você é um diretor avaliando a comunicação escrita de um aprendiz.

Analise o texto abaixo com linguagem objetiva e profissional.

Responda exatamente neste formato:

Acertou em:
- ...

Precisa melhorar em:
- ...

Avaliação geral:
- ...

Regras:
- Seja conciso.
- Não reescreva o texto.
- Não dê modelo pronto.
- Não forneça exemplo de correção.
- Foque em português, clareza, organização e tom profissional.

Texto do aprendiz:
{texto_1}
"""

                    feedback = chamar_gemini(prompt, api_key)

                    st.subheader("📋 Avaliação do Diretor:")
                    st.write(feedback)

                    status = "Registrado"

                    dados = {
                        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "nome": nome,
                        "tema": "Comunicação Empresarial",
                        "missao": "Comunicado Interno",
                        "tentativa": st.session_state.tentativa_1,
                        "resposta_aluno": texto_1,
                        "feedback_ia": feedback,
                        "status": status
                    }

                    ok, mensagem = salvar_planilha(dados, webhook_url)

                    if ok:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)

                    st.session_state.tentativa_1 += 1

    with tab2:
        st.info("**SITUAÇÃO:** Digitalização. Informe ao cliente que as faturas agora serão enviadas apenas em PDF.")

        texto_2 = st.text_area("Redija o e-mail para o cliente:", height=180, key="t2")

        if st.button("Enviar para Avaliação (Desafio 2)"):
            if not texto_2.strip():
                st.warning("Digite o texto antes de enviar.")
            else:
                with st.spinner("Analisando atendimento..."):

                    prompt = f"""
Você é um diretor avaliando a comunicação escrita de um aprendiz.

Analise o texto abaixo com linguagem objetiva e profissional.

Responda exatamente neste formato:

Acertou em:
- ...

Precisa melhorar em:
- ...

Avaliação geral:
- ...

Regras:
- Seja conciso.
- Não reescreva o texto.
- Não dê modelo pronto.
- Não forneça exemplo de correção.
- Foque em português, clareza, organização, cordialidade e tom profissional para cliente externo.

Texto do aprendiz:
{texto_2}
"""

                    feedback = chamar_gemini(prompt, api_key)

                    st.subheader("📋 Avaliação do Diretor:")
                    st.write(feedback)

                    status = "Registrado"

                    dados = {
                        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "nome": nome,
                        "tema": "Comunicação Empresarial",
                        "missao": "Comunicado Externo",
                        "tentativa": st.session_state.tentativa_2,
                        "resposta_aluno": texto_2,
                        "feedback_ia": feedback,
                        "status": status
                    }

                    ok, mensagem = salvar_planilha(dados, webhook_url)

                    if ok:
                        st.success(mensagem)
                    else:
                        st.error(mensagem)

                    st.session_state.tentativa_2 += 1

else:
    st.warning("👈 Identifique-se na barra lateral para começar a aula.")

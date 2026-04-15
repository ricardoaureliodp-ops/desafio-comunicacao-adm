import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO COM A IA (SÓ CRÍTICA, SEM SUGESTÃO) ---
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
    except: return "O Diretor está ocupado. Tente novamente."

# --- 2. SALVAR NA PLANILHA (Ajuste reforçado para a Assinatura) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        with open('credentials.json') as f:
            info = json.load(f)
        
        # Limpeza robusta: Garante que a chave privada seja lida corretamente pelo Google
        key = info['private_key']
        if "\\n" in key:
            key = key.replace("\\n", "\n")
        info['private_key'] = key
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Mostra o erro na lateral para sabermos se a assinatura passou
        st.sidebar.error(f"Erro de Gravação: {e}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES (FOCO NO APRENDIZ) ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# REGRAS DO DIRETOR: SÓ CRÍTICAS, NADA DE DAR A RESPOSTA PRONTA
comando_diretor = (
    "Aja como um Diretor Administrativo extremamente exigente e focado em resultados. "
    "Sua função é avaliar a comunicação de um Jovem Aprendiz. "
    "REGRAS OBRIGATÓRIAS: "
    "1. Analise apenas os erros de português, o tom de voz e a etiqueta profissional. "
    "2. SEJA DIRETO: diga o que está ruim e por que está inadequado para uma empresa. "
    "3. PROIBIÇÃO ABSOLUTA: Não forneça sugestões de texto pronto, não escreva 'versão ideal' e não dê exemplos de como deveria ser. "
    "4. Deixe que o aluno descubra como melhorar sozinho com base na sua crítica. "
    "5. No final, dê uma nota de 0 a 10. Se a nota for abaixo de 7, diga: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Limpar e Reiniciar"): st.session_state.clear(); st.rerun()

if nome:
    tab1, tab2 = st.tabs(["📧 E-mail Interno (VR)", "🤝 E-mail Externo (PDF)"])

    with tab1:
        st.info("**SITUAÇÃO:** O VR (Vale Refeição) aumentou 10%. Os novos cartões estão na Recepção. Retirada apenas sexta.")
        texto_1 = st.text_area("Redija o comunicado interno:", key="t1", height=150)
        if st.button("Enviar Desafio 1"):
            with st.spinner("O Diretor está lendo..."):
                prompt = f"{comando_diretor}\n\nTexto do Aluno {nome}:\n'{texto_1}'"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.info("**SITUAÇÃO:** Faturas agora são apenas por E-mail (PDF). Peça confirmação dos dados ao cliente.")
        texto_2 = st.text_area("Redija o e-mail para o cliente:", key="t2", height=150)
        if st.button("Enviar Desafio 2"):
            with st.spinner("O Diretor está analisando..."):
                prompt = f"{comando_diretor}\n\nTexto do Aluno {nome}:\n'{texto_2}'"
                res = chamar_gemini(prompt, api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Identifique-se na lateral para iniciar.")

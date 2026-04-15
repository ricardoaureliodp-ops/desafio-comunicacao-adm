import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO COM A IA (SÓ CRÍTICA, SEM RESPOSTA PRONTA) ---
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

# --- 2. SALVAR NA PLANILHA (LIMPEZA REFORÇADA DE CHAVE) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo o arquivo e limpando a chave de forma agressiva
        with open('credentials.json', 'r') as f:
            creds_info = json.load(f)
        
        # O segredo: Limpa espaços, quebras de linha duplicadas e caracteres de escape
        raw_key = creds_info['private_key']
        clean_key = raw_key.replace('\\n', '\n').strip()
        creds_info['private_key'] = clean_key
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Mostra o erro real na barra lateral para sabermos o que houve
        st.sidebar.error(f"Erro de Gravação: {str(e)}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES DETALHADAS PARA O ALUNO ---
st.set_page_config(page_title="Simulador Profissional", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# PROMPT DO DIRETOR: CRÍTICO E SEM DAR O PEIXE
regra_diretor = (
    "Aja como um Diretor Administrativo extremamente rigoroso e impaciente com erros básicos. "
    "Avalie o e-mail de um Jovem Aprendiz. "
    "REGRAS OBRIGATÓRIAS: "
    "1. NÃO dê a resposta correta. "
    "2. NÃO escreva 'A forma correta seria...' ou sugestões de texto pronto. "
    "3. APONTE APENAS OS ERROS: gramática, uso de gírias, falta de educação ou tom inadequado. "
    "4. Se o aluno escreveu tudo em maiúsculas, diga que ele está gritando e isso é inaceitável. "
    "Finalize com uma nota de 0 a 10. Se a nota for menor que 7, escreva: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Limpar e Reiniciar"): 
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Siga as instruções e redija os e-mails:")
    tab1, tab2 = st.tabs(["📧 Missão 1: E-mail Interno", "🤝 Missão 2: E-mail Externo"])

    with tab1:
        st.markdown("""
        **SITUAÇÃO:** Comunicado sobre o VR (Vale Refeição).
        
        **O que é VR?** É o benefício que a empresa deposita num cartão para você pagar seu almoço.
        **O Contexto:** O valor do VR da nossa empresa aumentou em **10%**. Os novos cartões já chegaram.
        
        **SUA TAREFA:** Escreva um e-mail para a equipe avisando que:
        1. O VR aumentou **10%**.
        2. Todos devem retirar o novo cartão na **Recepção**.
        3. A retirada deve ser feita **somente nesta sexta-feira**.
        
        *Lembre-se: Use um tom profissional, com saudação e despedida.*
        """)
        texto_1 = st.text_area("Redija seu e-mail interno aqui:", key="t1", height=200)
        if st.button("Enviar para Crítica do Diretor (1)"):
            with st.spinner("O Diretor está analisando..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.markdown("""
        **SITUAÇÃO:** Modernização - Boletos em PDF.
        
        **O Contexto:** A empresa agora é digital e sustentável. Não enviaremos mais faturas de papel pelo correio.
        
        **SUA TAREFA:** Escreva para um cliente informando que:
        1. A partir do mês que vem, as faturas serão enviadas apenas por **E-mail (PDF)**.
        2. Peça para o cliente **confirmar** se o e-mail de cadastro dele está correto.
        
        *Lembre-se: O cliente é a pessoa mais importante para a empresa. Seja muito educado!*
        """)
        texto_2 = st.text_area("Redija seu e-mail para o cliente aqui:", key="t2", height=200)
        if st.button("Enviar para Crítica do Diretor (2)"):
            with st.spinner("Analisando seu atendimento..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Digite seu nome na barra lateral para começar a aula.")

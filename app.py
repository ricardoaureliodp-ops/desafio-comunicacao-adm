import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO COM A IA (SÓ CRÍTICA, SEM DAR A RESPOSTA) ---
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
    except: return "O Diretor está ocupado. Tente de novo."

# --- 2. SALVAR NA PLANILHA (LIMPEZA DEFINITIVA DA CHAVE) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo o arquivo JSON
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # LIMPEZA BRUTA: Corrige a chave para o formato que o Google exige
        # Isso mata o erro 'Invalid JWT Signature'
        raw_key = creds_data['private_key']
        if "\\n" in raw_key:
            clean_key = raw_key.replace('\\n', '\n')
        else:
            clean_key = raw_key
        
        creds_data['private_key'] = clean_key
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
        client = gspread.authorize(creds)
        
        # Abre a sua planilha
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Se der erro, ele aparece na lateral para você ler
        st.sidebar.error(f"Erro de Gravação: {str(e)}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES DETALHADAS ---
st.set_page_config(page_title="Simulador Profissional", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# PROMPT DO DIRETOR: SÓ CRÍTICAS, NADA DE RESPOSTA PRONTA
regra_diretor = (
    "Aja como um Diretor Administrativo extremamente rígido, sem paciência para amadorismo. "
    "Sua única função é CRITICAR e APONTAR OS ERROS do e-mail do aprendiz. "
    "REGRAS ABSOLUTAS: "
    "1. NÃO dê a resposta correta e NÃO mostre como o e-mail deveria ser. "
    "2. NÃO dê sugestões de texto, NÃO use frases como 'O ideal seria...' ou 'Você poderia escrever assim...'. "
    "3. APONTE APENAS OS ERROS: erros de português, tom de voz inadequado, falta de clareza ou falta de educação. "
    "4. Seja curto e grosso na crítica. Deixe que o aluno pense e descubra a solução sozinho. "
    "Finalize com uma nota de 0 a 10. Se a nota for menor que 7, escreva: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Limpar e Reiniciar"): 
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Leia as instruções e cumpra as missões:")
    tab1, tab2 = st.tabs(["📧 Missão 1: E-mail Interno", "🤝 Missão 2: E-mail Externo"])

    with tab1:
        st.markdown("""
        **SITUAÇÃO:** Comunicado sobre o **VR (Vale Refeição)**.
        
        **O que é VR?** É um benefício que a empresa dá em um cartão para você pagar seu almoço em restaurantes.
        
        **O Contexto:** A empresa aumentou o valor do VR em **10%**. Os novos cartões já chegaram.
        
        **SUA TAREFA:** Escreva um e-mail para todos os seus colegas de equipe informando que:
        1. O valor do VR subiu **10%**.
        2. Todos devem retirar o novo cartão na **Recepção**.
        3. A retirada deve ser feita **somente nesta sexta-feira**.
        
        *Lembre-se: Use um tom profissional, com saudação no início e despedida no final.*
        """)
        texto_1 = st.text_area("Redija seu e-mail interno aqui:", key="t1", height=200)
        if st.button("Enviar para Avaliação (1)"):
            with st.spinner("O Diretor está analisando..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.markdown("""
        **SITUAÇÃO:** Modernização - **Boleto por E-mail (PDF)**.
        
        **O Contexto:** A empresa agora é digital e sustentável. Não enviaremos mais faturas de papel pelo correio.
        
        **SUA TAREFA:** Escreva para um cliente informando que:
        1. A partir do próximo mês, as faturas serão enviadas **apenas por E-mail (PDF)**.
        2. Peça para o cliente **confirmar** se o e-mail de cadastro dele está correto.
        
        *Lembre-se: O cliente é fundamental. Seja muito cordial e educado.*
        """)
        texto_2 = st.text_area("Redija seu e-mail para o cliente aqui:", key="t2", height=200)
        if st.button("Enviar para Avaliação (2)"):
            with st.spinner("O Diretor está analisando seu atendimento..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Digite seu nome na lateral para começar.")

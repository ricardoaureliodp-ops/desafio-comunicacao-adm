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

# --- 2. SALVAR NA PLANILHA (LIMPEZA TOTAL DE CHAVE) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo o arquivo JSON
        with open('credentials.json', 'r') as f:
            creds_info = json.load(f)
        
        # LIMPEZA AGRESSIVA: Corrige a chave para o formato aceito pelo Google
        # Remove espaços extras e garante que as quebras de linha sejam reais
        raw_key = creds_info['private_key']
        clean_key = raw_key.replace('\\n', '\n').strip()
        creds_info['private_key'] = clean_key
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        
        # Tenta abrir a planilha pelo nome exato
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Mostra o erro exato na barra lateral para diagnóstico
        st.sidebar.error(f"Erro ao salvar na planilha: {str(e)}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES DETALHADAS ---
st.set_page_config(page_title="Simulador Profissional", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# PROMPT DO DIRETOR: CRÍTICO, EXIGENTE E SEM DAR O PEIXE
regra_diretor = (
    "Aja como um Diretor Administrativo extremamente rígido, formal e direto ao ponto. "
    "Sua função é APENAS CRITICAR e APONTAR OS ERROS do e-mail de um Jovem Aprendiz. "
    "REGRAS ABSOLUTAS: "
    "1. NÃO dê a resposta correta ou sugestões de como escrever. "
    "2. NÃO escreva 'A forma correta seria...' ou 'Você deveria ter dito...'. "
    "3. NÃO dê exemplos de frases ou versões ideais. "
    "4. Apenas aponte os erros de português, o tom inadequado, o uso de gírias e a falta de etiqueta empresarial. "
    "Se a nota for menor que 7, termine com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Limpar e Reiniciar"): 
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Leia as instruções com atenção:")
    tab1, tab2 = st.tabs(["📧 Missão 1: E-mail Interno", "🤝 Missão 2: E-mail Externo"])

    with tab1:
        st.markdown("""
        ### Missão 1: Comunicado de Benefício (VR)
        **O Contexto:** O valor do VR (Vale Refeição - dinheiro para almoço) aumentou em **10%**. Os novos cartões já estão disponíveis.
        
        **SUA TAREFA:** Escreva um e-mail para todos os seus colegas de equipe informando que:
        1. O VR aumentou **10%**.
        2. Todos devem retirar o novo cartão na **Recepção**.
        3. A retirada deve ser feita **somente nesta sexta-feira**.
        
        *Dica: Use um tom profissional. Lembre-se da saudação inicial e da despedida.*
        """)
        texto_1 = st.text_area("Redija o e-mail interno aqui:", key="t1", height=200)
        if st.button("Enviar para Avaliação (Missão 1)"):
            with st.spinner("O Diretor está analisando sua postura..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.markdown("""
        ### Missão 2: Modernização - Fatura Digital
        **O Contexto:** A empresa agora é 100% digital e sustentável. Não enviaremos mais faturas em papel.
        
        **SUA TAREFA:** Escreva para um cliente informando que:
        1. A partir do próximo mês, as faturas serão enviadas apenas por **E-mail (em PDF)**.
        2. Peça para o cliente **confirmar** se o e-mail de cadastro dele está correto.
        
        *Dica: O cliente é vital para o negócio. Seja muito cordial e educado.*
        """)
        texto_2 = st.text_area("Redija o e-mail para o cliente aqui:", key="t2", height=200)
        if st.button("Enviar para Avaliação (Missão 2)"):
            with st.spinner("Analisando seu atendimento ao cliente..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Digite seu nome na barra lateral para começar a aula.")

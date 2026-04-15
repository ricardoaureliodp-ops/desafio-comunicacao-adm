import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXÃO IA (FEEDBACK DETALHADO E RÍGIDO) ---
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
        
        # O FIX DEFINITIVO: Garante que a chave privada não tenha caracteres invisíveis
        raw_key = creds_info['private_key']
        # Remove barras invertidas duplas e limpa espaços
        clean_key = raw_key.replace('\\n', '\n').replace(' ', '').replace('-----BEGINPRIVATEKEY-----', '-----BEGIN PRIVATE KEY-----').replace('-----ENDPRIVATEKEY-----', '-----END PRIVATE KEY-----')
        
        # Se por acaso o replace acima tirou espaços demais do miolo da chave, vamos usar a forma mais segura:
        creds_info['private_key'] = raw_key.replace('\\n', '\n')
            
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        st.sidebar.error(f"Erro de Gravação: {str(e)}")
        return False

# --- 3. INTERFACE E ORIENTAÇÕES PARA O ALUNO ---
st.set_page_config(page_title="Simulador Administrativo", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

api_key = st.secrets.get("GEMINI_API_KEY")

# PROMPT DO DIRETOR: DETALHISTA E IMPLACÁVEL
regra_diretor = (
    "Aja como um Diretor Administrativo sênior, extremamente exigente e culto. "
    "Sua tarefa é fazer uma CRÍTICA PEDAGÓGICA E DETALHADA do e-mail de um Jovem Aprendiz. "
    "REGRAS OBRIGATÓRIAS: "
    "1. ANALISE TUDO: Se o aluno usar CAIXA ALTA (letras maiúsculas), explique que isso equivale a GRITAR e é uma falta de respeito grave. "
    "2. RECLAME de gírias como 'LINDOS', 'AMORES', 'VIU', 'PEGA AÍ'. "
    "3. EXIJA saudação (Ex: Prezados) e despedida profissional. "
    "4. NÃO DÊ O TEXTO PRONTO. O aluno deve aprender com a sua crítica e tentar de novo. "
    "5. Use tópicos para facilitar a leitura. "
    "No final, dê uma nota de 0 a 10. Se a nota for menor que 7, termine com: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."
)

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Reiniciar"): 
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Missões de hoje:")
    tab1, tab2 = st.tabs(["📧 Missão 1: E-mail Interno", "🤝 Missão 2: E-mail Externo"])

    with tab1:
        st.markdown("""
        **SITUAÇÃO:** O VR (Vale Refeição) aumentou em 10%.
        **O QUE FAZER:** Avise os colegas para buscarem os novos cartões na Recepção apenas nesta sexta.
        *Atenção: Use tom profissional, sem gírias e sem gritar (caixa alta).*
        """)
        texto_1 = st.text_area("Digite o e-mail interno:", key="t1", height=200)
        if st.button("Enviar para Avaliação (1)"):
            with st.spinner("O Diretor está analisando..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_1}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Interno (VR)", res)

    with tab2:
        st.markdown("""
        **SITUAÇÃO:** Faturas agora são apenas por E-mail (PDF).
        **O QUE FAZER:** Informe o cliente e peça confirmação dos dados.
        *Dica: Seja extremamente educado e formal. O cliente é a imagem da empresa.*
        """)
        texto_2 = st.text_area("Digite o e-mail para o cliente:", key="t2", height=200)
        if st.button("Enviar para Avaliação (2)"):
            with st.spinner("Analisando atendimento..."):
                res = chamar_gemini(f"{regra_diretor}\n\nTexto de {nome}: '{texto_2}'", api_key)
                st.subheader("📋 Crítica do Diretor:")
                st.write(res)
                salvar_resultado(nome, "Externo (PDF)", res)
else:
    st.warning("👈 Digite seu nome na lateral.")

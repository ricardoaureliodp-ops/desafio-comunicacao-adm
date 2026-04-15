import streamlit as st
import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. FUNÇÃO DE CONEXÃO COM O GEMINI (IA) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: Chave API não encontrada nos Secrets."
    
    # Busca automática do modelo disponível
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash"
    
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo_final = m['name']
                    if "flash" in m['name']:
                        break
    except:
        pass

    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url_chat, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"O Diretor está ocupado (Erro {r.status_code})."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- 2. FUNÇÃO DE SALVAMENTO NA PLANILHA (O FIX DO ERRO) ---
def salvar_resultado(nome, atividade, feedback):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo o arquivo JSON e limpando a chave privada para evitar 'Invalid JWT Signature'
        with open('credentials.json') as f:
            info = json.load(f)
        
        # Este comando corrige a assinatura digital do robô
        info['private_key'] = info['private_key'].replace('\\n', '\n')
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        client = gspread.authorize(creds)
        
        # Abre a planilha pelo nome exato
        sheet = client.open("SIMULADOR_COMUNICACAO_2026").sheet1
        sheet.append_row([nome, atividade, feedback])
        return True
    except Exception as e:
        # Se der erro, ele avisa na barra lateral
        st.sidebar.error(f"Erro ao salvar na planilha: {e}")
        return False

# --- 3. CONFIGURAÇÃO DA INTERFACE DO JOGO ---
st.set_page_config(page_title="Simulador Jovem Aprendiz", layout="wide")
st.title("💼 Simulador de Comunicação Profissional")

# Puxa a chave secreta do Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

# Regra para a IA forçar o aluno a refazer se estiver ruim
regra_redo = "⚠️ IMPORTANTE: Se o texto for informal demais ou com erros graves, termine obrigatoriamente com a frase: '⚠️ ATENÇÃO: padrão insuficiente. REFAÇA O E-MAIL.'."

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Seu Nome Completo:")
    if st.button("Reiniciar Simulador"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Bem-vindo, {nome}! Escolha sua missão de hoje:")
    tab1, tab2 = st.tabs(["📧 E-mail Interno (Equipe)", "🤝 E-mail Externo (Cliente)"])

    with tab1:
        st.markdown("""
        ### Missão 1: Comunicado de Benefício (VR)
        **O que é VR?** Significa **Vale Refeição**. É o valor que a empresa dá para você almoçar.
        **Cenário:** O valor do VR aumentou em **10%**!
        **Tarefa:** Avise seus colegas que o aumento chegou e que devem buscar os novos cartões na **Recepção** apenas nesta **sexta-feira**.
        """)
        texto_1 = st.text_area("Redija o e-mail interno aqui:", key="t1", height=150)
        if st.button("Enviar para o Diretor (Missão 1)"):
            with st.spinner("O Diretor está analisando..."):
                prompt = f"Aja como um Diretor Administrativo. Avalie o e-mail de {nome}: '{texto_1}'. {regra_redo}"
                feedback = chamar_gemini(prompt, api_key)
                st.subheader("📋 Avaliação do Diretor:")
                st.write(feedback)
                salvar_resultado(nome, "E-mail Interno (VR)", feedback)

    with tab2:
        st.markdown("""
        ### Missão 2: Boletos em PDF
        **Cenário:** A empresa agora é digital! Não enviaremos mais boletos de papel.
        **Tarefa:** Escreva para um cliente informando que, a partir do mês que vem, as contas serão enviadas apenas por **E-mail (PDF)**. Peça para ele confirmar os dados.
        """)
        texto_2 = st.text_area("Redija o e-mail para o cliente aqui:", key="t2", height=150)
        if st.button("Enviar para o Diretor (Missão 2)"):
            with st.spinner("Analisando atendimento..."):
                prompt = f"Avalie o português e o tom profissional deste e-mail de {nome} para um cliente: '{texto_2}'. {regra_redo}"
                feedback = chamar_gemini(prompt, api_key)
                st.subheader("📋 Avaliação do Diretor:")
                st.write(feedback)
                salvar_resultado(nome, "E-mail Externo (PDF)", feedback)
else:
    st.warning("👈 Digite seu nome completo na barra lateral para começar a aula.")

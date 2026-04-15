import streamlit as st
import requests

# --- 1. CÓDIGO BLINDADO (AUTO-DETECT CONFORME SEU PDF) --- [cite: 103, 106]
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: Chave API não configurada nos Secrets."

    # 1. Pergunta ao Google quais modelos sua chave pode usar [cite: 107-108]
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo_final = "models/gemini-1.5-flash" # Modelo padrão de segurança [cite: 109]
    
    try:
        res = requests.get(url_list, timeout=10) [cite: 111]
        if res.status_code == 200:
            modelos_disponiveis = res.json().get('models', []) [cite: 112]
            for m in modelos_disponiveis:
                # Procura um modelo que aceite gerar conteúdo [cite: 113, 116]
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo_final = m['name'] [cite: 117]
                    # Prioriza o flash se ele estiver na lista
                    if "flash" in m['name']:
                        break
    except:
        pass # Se falhar a listagem, tenta usar o padrão [cite: 115]

    # 2. Faz a chamada oficial para o endereço que o Google liberou [cite: 118-120]
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo_final}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]} [cite: 121]
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15) [cite: 122]
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text'] [cite: 123]
        else:
            return f"O Diretor está ocupado (Erro {r.status_code}). Tente novamente."
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- 2. INTERFACE PEDAGÓGICA (O QUE O ALUNO VÊ) ---
st.set_page_config(page_title="Simulador de Comunicação", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

# Puxa a chave dos Secrets do Streamlit [cite: 91, 95]
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Jogo"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"### Olá, {nome}! Escolha seu desafio de hoje:")
    
    tab1, tab2 = st.tabs(["📧 Comunicado Interno", "🤝 Comunicado Externo"])

    with tab1:
        st.info("""
        **SITUAÇÃO:** Aviso de Benefício para a Equipe.
        **Tarefa:** Redija um e-mail informando que o Vale Refeição aumentou 10% e que os novos cartões devem ser retirados na Recepção nesta sexta-feira.
        **O que será avaliado:** Uso correto do Português, tom de voz profissional e clareza nas informações.
        """)
        texto_1 = st.text_area("Redija seu e-mail aqui:", height=180, key="t1")
        if st.button("Enviar para o Diretor (Desafio 1)"):
            with st.spinner("Analisando sua escrita..."):
                prompt = f"""
                Você é um Diretor Administrativo rigoroso. Analise o e-mail do aprendiz {nome}:
                '{texto_1}'
                
                Forneça um feedback completo cobrindo:
                1. ERROS DE PORTUGUÊS: Verifique ortografia e gramática.
                2. CONCEITOS ADMINISTRATIVOS: Avalie o tom e se todas as informações obrigatórias foram incluídas.
                3. RECOMENDAÇÃO: Dê uma nota de 0 a 10 e mostre como seria a versão perfeita.
                """
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))

    with tab2:
        st.info("""
        **SITUAÇÃO:** Modernização de Processos (Digitalização).
        **Tarefa:** Informe a um cliente que as faturas agora serão enviadas apenas por E-mail (PDF). Peça para ele confirmar o e-mail de recebimento.
        **O que será avaliado:** Cordialidade com o cliente e precisão técnica.
        """)
        texto_2 = st.text_area("Redija o e-mail para o cliente:", height=180, key="t2")
        if st.button("Enviar para o Diretor (Desafio 2)"):
            with st.spinner("O Diretor está avaliando seu atendimento..."):
                prompt = f"Analise o português e o tom administrativo deste e-mail para um cliente: {texto_2}. Seja detalhista no feedback para o aluno {nome}."
                st.subheader("📋 Avaliação do Diretor:")
                st.write(chamar_gemini(prompt, api_key))
else:
    st.warning("👈 Identifique-se na barra lateral para começar a aula.")

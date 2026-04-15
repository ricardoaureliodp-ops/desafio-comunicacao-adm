import streamlit as st
import requests

# --- 1. CÓDIGO BLINDADO (AUTO-DETECT DA IA) ---
def chamar_gemini(prompt, api_key):
    if not api_key:
        return "Erro: Chave API não encontrada. Configure os Secrets no Streamlit."

    # 1. Pergunta quais modelos estão liberados
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    modelo = "models/gemini-1.5-flash" # Padrão
    
    try:
        res = requests.get(url_list, timeout=10)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    modelo = m['name']
                    break
    except:
        pass # Se falhar a listagem, segue com o modelo padrão

    # 2. Faz a chamada oficial
    url_chat = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        r = requests.post(url_chat, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na conexão (Status {r.status_code}). O Google recusou a chamada."
    except Exception as e:
        return f"Erro inesperado de rede: {str(e)}"


# --- 2. INTERFACE DO SIMULADOR (COMUNICAÇÃO) ---
st.set_page_config(page_title="Treinamento Executivo", page_icon="💼", layout="wide")
st.title("💼 Simulador de Comunicação Empresarial")

# Puxa a chave dos Secrets do Streamlit de forma segura
api_key = st.secrets.get("GEMINI_API_KEY")

# Identificação na Barra Lateral
with st.sidebar:
    st.header("🏢 Portal do Colaborador")
    nome = st.text_input("Nome do Aprendiz:")
    if st.button("Reiniciar Simulador"):
        st.session_state.clear()
        st.rerun()

if nome:
    st.write(f"Bem-vindo(a) ao setor administrativo, **{nome}**. Hoje você tem duas missões importantes de comunicação. Escolha uma abaixo para começar:")
    
    tab1, tab2 = st.tabs(["📧 Desafio 1: E-mail Interno", "🤝 Desafio 2: E-mail Externo"])

    # DESAFIO 1
    with tab1:
        st.info("**SITUAÇÃO:** Você precisa avisar todos os funcionários que o Vale Refeição (VR) aumentou em 10% e os novos cartões devem ser retirados na Recepção na sexta-feira.")
        texto_interno = st.text_area("Redija seu e-mail para os funcionários:", height=200, key="interno")
        
        if st.button("Enviar para o Diretor (Desafio 1)"):
            if texto_interno:
                with st.spinner("O Diretor está avaliando sua escrita..."):
                    prompt = f"""
                    Aja como um Diretor Administrativo muito exigente. Avalie este e-mail interno escrito pelo jovem aprendiz {nome}:
                    '{texto_interno}'
                    
                    Forneça um feedback detalhado com a seguinte estrutura:
                    1. 📝 PORTUGUÊS: Aponte erros de gramática, ortografia, concordância ou pontuação.
                    2. 💼 CONCEITOS ADMINISTRATIVOS: Faltou alguma informação (10%, sexta-feira, recepção)? O tom está profissional? Faltou saudação ou despedida?
                    3. ✨ SUGESTÃO DE MELHORIA: Reescreva o e-mail de forma exemplar.
                    """
                    resposta = chamar_gemini(prompt, api_key)
                    st.success("Avaliação Concluída!")
                    st.write(resposta)
            else:
                st.warning("Escreva o e-mail antes de enviar.")

    # DESAFIO 2
    with tab2:
        st.info("**SITUAÇÃO:** Informe a um cliente importante que, a partir do próximo mês, as Notas Fiscais e Boletos não serão mais enviados por correio físico, apenas por E-mail (PDF). Peça para ele confirmar se o e-mail do cadastro está correto.")
        texto_externo = st.text_area("Redija seu e-mail para o cliente:", height=200, key="externo")
        
        if st.button("Enviar para o Diretor (Desafio 2)"):
            if texto_externo:
                with st.spinner("O Diretor está avaliando seu atendimento ao cliente..."):
                    prompt = f"""
                    Aja como um Diretor Administrativo muito exigente. Avalie este e-mail externo para um cliente escrito pelo jovem aprendiz {nome}:
                    '{texto_externo}'
                    
                    Forneça um feedback detalhado com a seguinte estrutura:
                    1. 📝 PORTUGUÊS: Aponte erros de gramática, ortografia, concordância ou pontuação.
                    2. 💼 CONCEITOS ADMINISTRATIVOS: O tom foi cordial com o cliente? A transição do meio físico para o digital (PDF) foi bem explicada? Solicitou a confirmação do e-mail de cadastro?
                    3. ✨ SUGESTÃO DE MELHORIA: Reescreva o e-mail de forma exemplar e voltada para excelência no atendimento.
                    """
                    resposta = chamar_gemini(prompt, api_key)
                    st.success("Avaliação Concluída!")
                    st.write(resposta)
            else:
                st.warning("Escreva o e-mail antes de enviar.")
else:
    st.warning("👈 Por favor, digite seu nome na barra lateral para liberar as tarefas do dia.")

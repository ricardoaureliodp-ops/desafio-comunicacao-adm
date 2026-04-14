import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO DA IA ---
# Sua chave já está configurada aqui
genai.configure(api_key="AIzaSyBMIsMJ9xfSW7IrJhhKGfq1D61dxsguIF8")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PERSONA DO CHEFE (BASEADO NO SEU SLIDE) ---
SISTEMA_PROMPT = """
Você é um Diretor Administrativo de uma grande corporação. Você é extremamente exigente com a qualidade dos textos, 
mas pratica rigorosamente a Comunicação Não-Violenta (CNV) e fornece feedbacks detalhados.

CRITÉRIOS DE AVALIAÇÃO (Obrigatórios):
1. COMUNICAÇÃO INTERNA: Tom direto e claro. Deve responder: O QUE, QUANDO e COMO ACESSAR.
2. COMUNICAÇÃO EXTERNA: Tom persuasivo e profissional. Foco total nos BENEFÍCIOS PARA O CLIENTE. Linguagem elaborada.

DINÂMICA:
- Analise o texto do aluno.
- Se faltar qualquer critério, aponte detalhadamente o que melhorar com educação (CNV).
- Se estiver perfeito, comece sua resposta EXATAMENTE com a palavra 'APROVADO'.
"""

st.set_page_config(page_title="Simulador de Comunicação Técnica", layout="centered")

st.title("💼 Desafio de Comunicação: Direção Executiva")
st.markdown("---")

# Controle de estado das fases
if 'fase' not in st.session_state:
    st.session_state.fase = 1

# --- FASE 1: INTERNA (Vale-Refeição) ---
if st.session_state.fase == 1:
    st.header("Fase 1: Comunicação Interna")
    st.info("SITUAÇÃO: O RH precisa informar sobre um novo benefício de vale-refeição.")
    st.write("**Instrução:** Seja direto e claro. Informe o que é, quando começa e como acessar.")
    
    texto_usuario = st.text_area("Digite sua proposta de e-mail interno:", height=200, key="txt_interna")
    
    if st.button("Enviar para o Diretor"):
        if texto_usuario:
            with st.spinner('O Diretor está analisando seu texto...'):
                res = model.generate_content(f"{SISTEMA_PROMPT}\n\nAnalise este e-mail INTERNO: {texto_usuario}")
                feedback = res.text
                
                if "APROVADO" in feedback.upper():
                    st.success("✅ APROVADO! Excelente trabalho de clareza.")
                    st.write(feedback.replace("APROVADO", ""))
                    if st.button("Ir para o Desafio Externo"):
                        st.session_state.fase = 2
                        st.rerun()
                else:
                    st.warning("⚠️ O Diretor solicitou melhorias:")
                    st.markdown(feedback)
        else:
            st.error("Por favor, escreva o texto antes de enviar.")

# --- FASE 2: EXTERNA (Novo Produto) ---
elif st.session_state.fase == 2:
    st.header("Fase 2: Comunicação Externa")
    st.info("SITUAÇÃO: A empresa está lançando um novo produto para os clientes.")
    st.write("**Instrução:** Use linguagem persuasiva e profissional. Foque nos benefícios para o cliente.")
    
    texto_usuario_ext = st.text_area("Digite seu e-mail de marketing:", height=200, key="txt_externa")
    
    if st.button("Finalizar Campanha"):
        if texto_usuario_ext:
            with st.spinner('O Diretor está avaliando o impacto comercial...'):
                res = model.generate_content(f"{SISTEMA_PROMPT}\n\nAnalise este e-mail EXTERNO: {texto_usuario_ext}")
                feedback_ext = res.text
                
                if "APROVADO" in feedback_ext.upper():
                    st.balloons()
                    st.success("✅ APROVADO! Sua comunicação externa atingiu o nível executivo.")
                    st.write(feedback_ext.replace("APROVADO", ""))
                else:
                    st.warning("⚠️ O Diretor acredita que pode ser mais persuasivo:")
                    st.markdown(feedback_ext)

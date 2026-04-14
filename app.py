import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO DA IA ---
genai.configure(api_key="AIzaSyBMIsMJ9xfSW7IrJhhKGfq1D61dxsguIF8")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- PERSONA DO CHEFE ---
SISTEMA_PROMPT = """
Você é o Diretor Executivo (CEO) de uma empresa de consultoria administrativa.
Seu perfil: Extremamente exigente com a escrita técnica, mas utiliza Comunicação Não-Violenta (CNV).

CRITÉRIOS DO MANUAL DA EMPRESA (SLIDE):
1. COMUNICAÇÃO INTERNA: Tom direto e claro. OBRIGATÓRIO: O QUE é o benefício, QUANDO começa e COMO acessar.
2. COMUNICAÇÃO EXTERNA: Tom persuasivo e profissional. Foco no BENEFÍCIO para o cliente. Linguagem elaborada.

INSTRUÇÃO:
- Se falhar nos critérios, dê feedback técnico detalhado.
- Só comece com 'APROVADO' se estiver perfeito conforme o manual.
"""

st.set_page_config(page_title="Simulador de Comunicação Técnica", layout="centered")

# --- CONTROLE DE SESSÃO ---
if 'nome' not in st.session_state:
    st.session_state.nome = ""
if 'fase' not in st.session_state:
    st.session_state.fase = 1

# --- TELA DE LOGIN/IDENTIFICAÇÃO ---
if not st.session_state.nome:
    st.title("💼 Sistema de Treinamento Executivo")
    st.subheader("Identificação do Colaborador")
    nome_input = st.text_input("Digite seu nome completo para acessar os desafios:")
    
    if st.button("Acessar Desafios"):
        if nome_input:
            st.session_state.nome = nome_input
            st.rerun()
        else:
            st.error("Por favor, identifique-se para que o Diretor possa avaliar seu desempenho.")

# --- INTERFACE DO JOGO (PÓS-LOGIN) ---
else:
    st.title("💼 Desafio de Comunicação: Direção Executiva")
    st.sidebar.markdown(f"👤 **Colaborador:**\n{st.session_state.nome}")
    
    if st.sidebar.button("Sair/Trocar Nome"):
        st.session_state.nome = ""
        st.session_state.fase = 1
        st.rerun()

    with st.expander("📢 MENSAGEM DA DIRETORIA", expanded=True):
        st.markdown(f"""
        **"Prezado(a) {st.session_state.nome},** como Diretor, prezo pela excelência. 
        Abaixo estão suas tarefas de hoje. Eu revisarei pessoalmente cada rascunho. 
        Siga rigorosamente o manual de comunicação da empresa (o slide) ou seu texto será rejeitado."
        """)

    st.markdown("---")

    # --- FASE 1: INTERNA ---
    if st.session_state.fase == 1:
        st.header("Fase 1: Comunicado Interno")
        st.info("SITUAÇÃO: Informar a equipe sobre o novo Vale-Refeição.")
        
        texto_usuario = st.text_area("Digite sua proposta de e-mail interno:", height=200, placeholder="Assunto: Atualização sobre Benefícios...")
        
        if st.button("Enviar para Revisão"):
            if texto_usuario:
                with st.spinner('O Diretor está analisando...'):
                    res = model.generate_content(f"{SISTEMA_PROMPT}\n\nAnalise este e-mail INTERNO: {texto_usuario}")
                    if "APROVADO" in res.text.upper():
                        st.success("✅ **APROVADO PELO DIRETOR!**")
                        st.write(res.text.replace("APROVADO", ""))
                        if st.button("Avançar para Fase Externa"):
                            st.session_state.fase = 2
                            st.rerun()
                    else:
                        st.warning("⚠️ **FEEDBACK DA DIRETORIA:**")
                        st.markdown(res.text)
            else:
                st.error("O campo de texto não pode estar vazio.")

    # --- FASE 2: EXTERNA ---
    elif st.session_state.fase == 2:
        st.header("Fase 2: Comunicação com o Mercado")
        st.info("SITUAÇÃO: Lançamento de um novo produto para os clientes.")
        
        texto_usuario_ext = st.text_area("Digite seu e-mail de marketing:", height=200, placeholder="Prezado cliente...")
        
        if st.button("Enviar para Aprovação Final"):
            if texto_usuario_ext:
                with st.spinner('Avaliando impacto comercial...'):
                    res = model.generate_content(f"{SISTEMA_PROMPT}\n\nAnalise este e-mail EXTERNO: {texto_usuario_ext}")
                    if "APROVADO" in res.text.upper():
                        st.balloons()
                        st.success("✅ **EXCELENTE! APROVADO PARA DISPARO AO MERCADO.**")
                        st.write(res.text.replace("APROVADO", ""))
                    else:
                        st.warning("⚠️ **FEEDBACK DA DIRETORIA:**")
                        st.markdown(res.text)

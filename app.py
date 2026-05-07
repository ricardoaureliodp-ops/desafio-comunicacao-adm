import streamlit as st
import requests
import base64
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# =========================================================
# CONSULTORIA FALA BONITO - COMUNICAÇÃO ORAL PROFISSIONAL
# Streamlit + Gemini API + Google Sheets via Apps Script
# Versão leve para sala: 2 casos, 2 tentativas e feedback curto
# =========================================================

st.set_page_config(
    page_title="Consultoria Fala Bonito",
    page_icon="🎤",
    layout="wide"
)

# -------------------- CONFIG --------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
# Aceita os dois nomes para evitar erro caso o Secret esteja com nome antigo ou novo
webhook_url = st.secrets.get("SHEETS_WEBHOOK_URL", st.secrets.get("WEBHOOK_URL", ""))

MAX_TENTATIVAS = 2

# -------------------- CASOS --------------------
casos = [
    {
        "nome": "Caso 1 - Apresentação Profissional",
        "contexto": "Imagine que você está iniciando uma reunião corporativa ou uma pequena apresentação profissional.",
        "tarefa": "Faça uma breve apresentação pessoal. Fale seu nome, sua área de atuação, experiências ou cargos que já exerceu, o motivo da reunião ou apresentação e finalize com uma saudação ao público.",
        "tempo": "Tempo sugerido: mínimo de 30 segundos e máximo de 1 minuto.",
        "foco": "Clareza, naturalidade, organização da fala, postura profissional e fechamento adequado.",
        "checklist": [
            "Diga seu nome com clareza.",
            "Informe sua área de atuação.",
            "Cite uma experiência, cargo ou responsabilidade profissional.",
            "Explique o motivo da reunião ou apresentação.",
            "Finalize com uma saudação cordial."
        ],
        "exemplo": "Boa tarde a todos. Meu nome é Ricardo, atuo na área administrativa e tenho experiência com atendimento, organização de processos e apoio à gestão. Já exerci funções ligadas ao controle de atividades e comunicação com equipes. O objetivo desta apresentação é compartilhar uma proposta de melhoria para o nosso trabalho. Agradeço a presença de todos."
    },
    {
        "nome": "Caso 2 - Cliente Insatisfeito",
        "contexto": "Você trabalha em uma empresa e um cliente entrou em contato insatisfeito por causa de um atraso em um serviço.",
        "tarefa": "Grave uma resposta profissional para esse cliente. Demonstre empatia, explique a situação sem criar conflito, apresente uma solução ou encaminhamento e finalize transmitindo confiança.",
        "tempo": "Tempo sugerido: mínimo de 40 segundos e máximo de 1 minuto e 30 segundos.",
        "foco": "Empatia, clareza, controle emocional, objetividade e linguagem profissional.",
        "checklist": [
            "Comece reconhecendo a insatisfação do cliente.",
            "Evite tom defensivo ou acusatório.",
            "Explique de forma simples o que será feito.",
            "Apresente um encaminhamento claro.",
            "Finalize com respeito e segurança."
        ],
        "exemplo": "Boa tarde. Compreendo sua insatisfação e peço desculpas pelo transtorno causado pelo atraso. Já estamos verificando a situação para resolver o quanto antes. A partir de agora, vou acompanhar seu atendimento e informar o prazo atualizado assim que a confirmação for concluída. Agradeço sua compreensão e reforço que estamos trabalhando para solucionar o caso com prioridade."
    }
]

# -------------------- FUNÇÕES --------------------
def escolher_modelos(api_key: str):
    """Lista modelos disponíveis e prioriza versões atuais da família Flash."""
    preferidos = []
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            modelos = r.json().get("models", [])
            nomes = [m.get("name", "") for m in modelos if "generateContent" in m.get("supportedGenerationMethods", [])]
            # Preferir modelos atuais; evitar modelos antigos 1.5 e 2.0, que deram erro para esta chave.
            for alvo in ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash"]:
                for nome in nomes:
                    n = nome.lower()
                    if alvo in n and "preview" not in n:
                        preferidos.append(nome)
                for nome in nomes:
                    n = nome.lower()
                    if alvo in n and "preview" in n:
                        preferidos.append(nome)
    except Exception:
        pass

    # Fallback principal atual
    fallback = ["models/gemini-2.5-flash"]
    lista = []
    for m in preferidos + fallback:
        if m and m not in lista:
            lista.append(m)
    return lista


def chamar_gemini_audio(prompt: str, audio_bytes: bytes, mime_type: str, api_key: str):
    if not api_key:
        return "ERRO_API_KEY"

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    ultimo_erro = ""

    for modelo in escolher_modelos(api_key):
        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": audio_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "topP": 0.8,
                "maxOutputTokens": 900
            }
        }

        try:
            r = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=70
            )

            if r.status_code == 200:
                data = r.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    return "ERRO_RESPOSTA_VAZIA"

            if r.status_code == 503:
                ultimo_erro = "ERRO_503"
                continue

            if r.status_code in [404, 429, 500]:
                ultimo_erro = f"{modelo} => ERRO_GEMINI_{r.status_code}: {r.text[:500]}"
                continue

            return f"{modelo} => ERRO_GEMINI_{r.status_code}: {r.text[:700]}"

        except Exception as e:
            ultimo_erro = f"ERRO_CONEXAO: {str(e)}"
            continue

    return ultimo_erro or "ERRO_CONEXAO"


def salvar_planilha(dados: dict, webhook_url: str):
    if not webhook_url:
        return False
    try:
        resposta = requests.post(webhook_url, json=dados, timeout=20)
        return resposta.status_code == 200
    except Exception:
        return False


def detectar_status(feedback: str, tentativa: int):
    texto = (feedback or "").lower()
    compacto = texto.replace(" ", "").replace("\n", "")
    if "status:satisfatório" in compacto or "status:podeavançar" in compacto or "status:aprovado" in compacto:
        return "Satisfatório"
    if "satisfatório" in texto and "precisa melhorar" not in texto:
        return "Satisfatório"
    if tentativa >= MAX_TENTATIVAS:
        return "Encerrado com orientação"
    return "Precisa melhorar"


def montar_prompt(caso: dict, tentativa: int, nome: str):
    exemplo_regra = ""
    if tentativa >= MAX_TENTATIVAS:
        exemplo_regra = f"""
Como esta é a última tentativa, se a fala ainda não estiver satisfatória, inclua obrigatoriamente um EXEMPLO CURTO de fala profissional para o aluno comparar. Use este modelo como referência, adaptando se necessário:
{caso['exemplo']}
"""
    else:
        exemplo_regra = "Na primeira tentativa, NÃO entregue exemplo pronto. Oriente o aluno para tentar melhorar."

    return f"""
Você é a Consultoria Fala Bonito, uma consultoria de comunicação oral para alunos de Técnico em Administração.
Analise o áudio enviado pelo aluno com foco em aprendizagem prática.

Aluno: {nome}
Caso: {caso['nome']}
Contexto: {caso['contexto']}
Tarefa esperada: {caso['tarefa']}
Tentativa atual: {tentativa} de {MAX_TENTATIVAS}

CRITÉRIOS:
- Clareza da mensagem
- Organização com começo, meio e fim
- Linguagem profissional
- Objetividade
- Naturalidade e ritmo da fala
- Adequação ao contexto do caso

REGRAS IMPORTANTES:
- Seja curto, direto e útil.
- Não faça introdução longa.
- Não escreva relatório extenso.
- Não humilhe o aluno.
- Valorize o que estiver bom.
- Explique claramente o que precisa melhorar.
- Se a fala estiver boa o suficiente para o contexto, libere avanço.
- Se estiver incompleta, vaga, confusa ou fora da tarefa, peça melhoria.
{exemplo_regra}

FORMATO OBRIGATÓRIO DA RESPOSTA:
Resumo da fala:
- escreva no máximo 2 linhas.

Pontos positivos:
- máximo 3 tópicos curtos.

O que melhorar:
- máximo 3 tópicos curtos, com orientação prática.

Dica para a próxima tentativa:
- 1 frase objetiva.

Exemplo profissional:
- preencher somente na última tentativa se ainda precisar melhorar; se estiver satisfatório, escreva: Não necessário.

Status:
- escreva exatamente uma destas opções: Satisfatório, Precisa melhorar ou Encerrado com orientação.
"""


def inicializar_estado():
    defaults = {
        "indice_caso": 0,
        "tentativa": 1,
        "ultimo_feedback": "",
        "ultimo_erro_tecnico": "",
        "caso_finalizado": False,
        "atividade_finalizada": False,
        "audio_bytes": None,
        "audio_mime": "audio/wav",
        "autoavaliacao": "",
        "gravador_key_id": 0
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def limpar_audio():
    st.session_state.audio_bytes = None
    st.session_state.audio_mime = "audio/wav"
    st.session_state.autoavaliacao = ""
    st.session_state.gravador_key_id += 1

# -------------------- INTERFACE --------------------
inicializar_estado()

with st.sidebar:
    st.header("👤 Identificação")
    nome = st.text_input("Nome do aluno:", key="nome_aluno")
    st.divider()
    st.write("🎧 Antes de enviar, ouça seu áudio. Se não gostar, apague e grave novamente.")
    with st.expander("⚙️ Opções avançadas"):
        confirmar = st.checkbox("Tenho certeza que quero reiniciar toda a atividade.")
        if st.button("Reiniciar atividade"):
            if confirmar:
                st.session_state.clear()
                st.rerun()
            else:
                st.warning("Marque a confirmação antes de reiniciar.")

st.title("🎤 Consultoria Fala Bonito - Comunicação Oral Profissional")
st.write("Atividade prática de comunicação oral com feedback curto, objetivo e orientador.")

if not nome:
    st.warning("👈 Digite seu nome na barra lateral para começar.")
    st.stop()

if st.session_state.atividade_finalizada:
    st.success("🎉 Parabéns! Você concluiu os dois desafios de comunicação oral.")
    st.info("Suas respostas foram registradas na planilha.")
    st.stop()

total_casos = len(casos)
caso = casos[st.session_state.indice_caso]

st.progress(st.session_state.indice_caso / total_casos)
st.write(f"### Progresso: Caso {st.session_state.indice_caso + 1} de {total_casos}")

with st.expander("ℹ️ Orientações gerais da atividade", expanded=False):
    st.write("""
Nesta atividade, você vai treinar comunicação oral profissional.

A proposta não é falar perfeito, mas melhorar clareza, organização, postura e segurança.

Antes de gravar:
- escreva um pequeno roteiro;
- leia em voz alta;
- treine uma vez;
- grave, escute e só envie quando achar adequado.

⚠️ Durante a análise do áudio, não atualize a página.
""")

st.subheader(f"📚 {caso['nome']}")
st.info(caso["contexto"])

col1, col2 = st.columns([1.6, 1])
with col1:
    st.write("### 🎯 Sua tarefa")
    st.write(caso["tarefa"])
    st.warning(caso["tempo"])
    st.write("### 🔎 Foco da avaliação")
    st.write(caso["foco"])

with col2:
    st.write("### ✅ Checklist antes de gravar")
    for item in caso["checklist"]:
        st.write(f"✔️ {item}")

st.divider()
st.write(f"## Tentativa atual: {st.session_state.tentativa} de {MAX_TENTATIVAS}")

if st.session_state.caso_finalizado:
    st.success("✅ Este caso foi encerrado. Clique em **Próximo caso** para continuar.")
elif st.session_state.tentativa == 1:
    st.info("🟢 Primeira tentativa: grave sua fala com clareza e profissionalismo.")
else:
    st.warning("🟡 Segunda tentativa: use o feedback anterior para melhorar. Se ainda não atingir o mínimo, a Consultoria trará um exemplo.")

# -------------------- GRAVAÇÃO --------------------
if not st.session_state.caso_finalizado:
    st.divider()
    st.subheader("🎙️ Gravação do áudio")
    st.caption("Permita o uso do microfone no navegador. Depois de gravar, ouça o áudio antes de enviar.")
    st.info("Use os botões abaixo para iniciar e parar a gravação. Depois, ouça seu áudio antes de enviar.")

    gravacao = mic_recorder(
        start_prompt="🎙️ Iniciar gravação",
        stop_prompt="⏹️ Parar gravação",
        just_once=False,
        use_container_width=True,
        key=f"gravador_{st.session_state.indice_caso}_{st.session_state.tentativa}_{st.session_state.gravador_key_id}"
    )

    if gravacao and isinstance(gravacao, dict) and gravacao.get("bytes"):
        st.session_state.audio_bytes = gravacao["bytes"]
        st.session_state.audio_mime = gravacao.get("mime_type", "audio/wav") or "audio/wav"

    if st.session_state.audio_bytes:
        st.success("Áudio gravado. Ouça antes de enviar.")
        st.audio(st.session_state.audio_bytes, format=st.session_state.audio_mime)

        st.write("Antes de enviar, como você avalia sua própria fala?")
        st.session_state.autoavaliacao = st.radio(
            "Autoavaliação",
            ["Muito nervoso(a)", "Razoável", "Confiante", "Ainda quero refazer"],
            horizontal=True,
            label_visibility="collapsed"
        )

        col_apagar, col_enviar = st.columns([1, 1])
        with col_apagar:
            if st.button("🗑️ Apagar e gravar novamente", use_container_width=True):
                limpar_audio()
                st.rerun()
        with col_enviar:
            enviar = st.button("📩 Enviar áudio para análise", use_container_width=True)

        if enviar:
            st.info("⏳ Envio recebido. A Consultoria Fala Bonito está analisando seu áudio. Aguarde sem atualizar a página.")
            with st.spinner("Analisando áudio... isso pode levar alguns segundos."):
                prompt = montar_prompt(caso, st.session_state.tentativa, nome)
                feedback = chamar_gemini_audio(
                    prompt,
                    st.session_state.audio_bytes,
                    st.session_state.audio_mime,
                    api_key
                )

            if feedback in ["ERRO_API_KEY", "ERRO_503", "ERRO_CONEXAO", "ERRO_RESPOSTA_VAZIA"] or str(feedback).startswith("ERRO") or "ERRO_GEMINI" in str(feedback):
                st.session_state.ultimo_erro_tecnico = feedback
                st.error("⚠️ A IA não conseguiu analisar agora ou ocorreu falha de conexão.")
                st.info("Não atualize a página. Sua gravação continua disponível. Clique novamente em **Enviar áudio para análise**. Esta tentativa não foi registrada, não foi salva na planilha e não contou como tentativa.")
                with st.expander("📄 Detalhe técnico para o professor"):
                    st.code(feedback)
                st.stop()

            st.session_state.ultimo_feedback = feedback
            status = detectar_status(feedback, st.session_state.tentativa)

            dados = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "nome": nome,
                "caso": caso["nome"],
                "tentativa": st.session_state.tentativa,
                "feedback": feedback,
                "status": status
            }

            salvou = salvar_planilha(dados, webhook_url)
            if not salvou:
                st.warning("O feedback apareceu, mas não foi possível salvar na planilha. Verifique o Apps Script ou a URL do webhook.")

            if status == "Satisfatório":
                st.session_state.caso_finalizado = True
                st.success("✅ Resposta satisfatória. Leia o feedback e clique em **Próximo caso** quando estiver pronto.")
                limpar_audio()
                st.rerun()
            elif st.session_state.tentativa >= MAX_TENTATIVAS:
                st.session_state.caso_finalizado = True
                st.warning("📌 Caso encerrado com orientação. Leia o feedback e clique em **Próximo caso** quando estiver pronto.")
                limpar_audio()
                st.rerun()
            else:
                st.session_state.tentativa += 1
                st.warning("Use o feedback para gravar uma nova tentativa.")
                limpar_audio()
                st.rerun()
    else:
        st.info("Grave seu áudio para liberar o envio à Consultoria Fala Bonito.")

# -------------------- FEEDBACK --------------------
if st.session_state.ultimo_feedback:
    st.divider()
    st.subheader("📋 Último feedback recebido")
    st.write(st.session_state.ultimo_feedback)

# -------------------- PRÓXIMO CASO --------------------
if st.session_state.caso_finalizado:
    st.divider()
    if st.session_state.indice_caso < total_casos - 1:
        if st.button("➡️ Próximo caso"):
            st.session_state.indice_caso += 1
            st.session_state.tentativa = 1
            st.session_state.ultimo_feedback = ""
            st.session_state.ultimo_erro_tecnico = ""
            st.session_state.caso_finalizado = False
            limpar_audio()
            st.rerun()
    else:
        if st.button("🏁 Finalizar atividade"):
            st.session_state.atividade_finalizada = True
            st.rerun()

import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. Configuração da Página ---
st.set_page_config(page_title="Chatbot com IA", page_icon="🤖")
st.title("🤖 Chatbot com Gatilhos de Venda")
st.caption("Um chat que interpreta a intenção do cliente e dispara alertas.")

# --- 2. Gerenciamento de Chaves (Seguro para Deploy) ---
def carregar_api_key():
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    return api_key

key = carregar_api_key()
if not key:
    st.error("Chave da API da OpenAI não encontrada! 😢")
    st.info("Configure a chave em 'Settings > Secrets' ou no arquivo .env.")
    st.stop()

try:
    client = OpenAI(api_key=key)
except Exception as e:
    st.error(f"Não foi possível inicializar o cliente da OpenAI: {e}")
    st.stop()

# --- 3. Carregamento das Instruções do Agente ---
try:
    with open('Instructions.txt', 'r', encoding='utf-8') as file:
        instructions = file.read()
except FileNotFoundError:
    st.error("Arquivo de instruções 'Banco de dados/Instructions.txt' não encontrado. 📄")
    st.stop()

# --- 4. Gerenciamento do Histórico da Conversa ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": instructions},
        {"role": "assistant", "content": "Olá! Sou o assistente de vendas da VIA PERSONNALITY. Como posso te ajudar hoje?"}
    ]

# --- 5. Exibição das Mensagens do Histórico ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 6. Lógica de Interação do Chat ---
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[msg for msg in st.session_state.messages]
                )
                resposta_completa = response.choices[0].message.content

                # --- NOVO: Lógica de Detecção e Processamento de Gatilhos ---
                mensagem_para_exibir = resposta_completa
                
                if "[GATILHO:FECHAMENTO]" in resposta_completa:
                    st.info(" GATILHO DETECTADO: Cliente demonstrou intenção de FECHAMENTO!")
                    mensagem_para_exibir = resposta_completa.replace("[GATILHO:FECHAMENTO]", "").strip()

                elif "[GATILHO:INSATISFACAO]" in resposta_completa:
                    st.warning(" GATILHO DETECTADO: Cliente demonstrou INSATISFAÇÃO ou agressividade!")
                    mensagem_para_exibir = resposta_completa.replace("[GATILHO:INSATISFACAO]", "").strip()

                elif "[GATILHO:COTACAO]" in resposta_completa:
                    st.success(" GATILHO DETECTADO: Cliente confirmou o desejo de COTAÇÃO!")
                    mensagem_para_exibir = resposta_completa.replace("[GATILHO:COTACAO]", "").strip()

                # Exibe a resposta limpa para o usuário
                st.markdown(mensagem_para_exibir)
                
                # Adiciona a resposta limpa ao histórico
                st.session_state.messages.append({"role": "assistant", "content": mensagem_para_exibir})

            except Exception as e:
                st.error(f"Ocorreu um erro ao contatar a API da OpenAI: {e}")



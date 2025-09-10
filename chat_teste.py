import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. Configuração da Página ---
st.set_page_config(page_title="Chatbot com IA", page_icon="🤖")
st.title("🤖 Chatbot com Instruções Customizadas")
st.caption("Um chat com memória que usa um arquivo de instruções para definir seu comportamento.")

# --- 2. Gerenciamento de Chaves (Seguro para Deploy) ---

# Esta função tenta buscar a chave da API de duas formas:
# 1. Dos "Secrets" do Streamlit (quando está no ar, no servidor)
# 2. De um arquivo .env (quando está rodando localmente na sua máquina)
def carregar_api_key():
    try:
        # Tenta pegar a chave dos secrets do Streamlit (ambiente de produção)
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Se não conseguir, carrega do .env (ambiente de desenvolvimento local)
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    return api_key

key = carregar_api_key()

if not key:
    st.error("Chave da API da OpenAI não encontrada! 😢")
    st.info("Se estiver rodando online, configure a chave em 'Settings > Secrets'. Se for localmente, verifique seu arquivo .env.")
    st.stop()

# Inicializa o cliente da OpenAI
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
    st.info("Verifique se o arquivo e a pasta existem no seu repositório do GitHub.")
    st.stop()

# --- 4. Gerenciamento do Histórico da Conversa ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": instructions},
        {"role": "assistant", "content": "Olá! Como posso te ajudar hoje?"}
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
                    messages=st.session_state.messages
                )
                resposta_assistente = response.choices[0].message.content
                st.markdown(resposta_assistente)
                st.session_state.messages.append({"role": "assistant", "content": resposta_assistente})
            except Exception as e:
                st.error(f"Ocorreu um erro ao contatar a API da OpenAI: {e}")



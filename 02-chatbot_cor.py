import os
from dotenv import load_dotenv
from openai import OpenAI
from colorama import Fore, Style, init

# Inicializando API Key da OpenAI
load_dotenv()                          # Carrega as variáveis do .env
api_key = os.getenv("OPENAI_API_KEY")  # Pega a chave da variável de ambiente
client = OpenAI(api_key=api_key)       # Cria o cliente com API KEY

# Inicializando o esquema de cores, a partir da biblioteca colorama
init(autoreset=True)

def geracao_texto(mensagens):
    resposta = client.chat.completions.create(
        messages=mensagens, 
        model="gpt-3.5-turbo-0125", 
        max_tokens=1000, 
        temperature=0,
        stream=True)
    
    print(f"{Fore.CYAN}Bot: ", end="")
    
    texto_completo = ""
    
    for resposta_stream in resposta:
        texto = resposta_stream.choices[0].delta.content
        if texto:
            print(texto, end="")
            texto_completo += texto
    print()
    mensagens.append({"role":"assistant", "content": texto_completo})
    return mensagens

if __name__ == "__main__":
    print(f"{Fore.YELLOW}Benvindo ao Chatbot")
    mensagens = []
    while True:
        in_user = input(f"{Fore.GREEN}User: {Style.RESET_ALL}")
        mensagens.append({"role":"user", "content": in_user})
        mensagens = geracao_texto(mensagens)
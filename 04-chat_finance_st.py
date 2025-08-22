import yfinance as yf
import openai
import json 
import streamlit as st
from dotenv import load_dotenv, find_dotenv

# Carregar as variáveis de ambiente: senhas e OPENAI_API_KEY
_ = load_dotenv(find_dotenv())

client = openai.Client()

def retorna_cotacao(ticker, periodo="1mo"):
    ticker_obj = f"{ticker}.SA"
    ativo = yf.Ticker(ticker_obj)
    hist = ativo.history(period=periodo)["Close"]
    hist.index = hist.index.strftime("Y%-%m-%d")
    hist = round(hist, 2)

    # Limitar o resultado a 30 registros
    if len(hist) > 30:
        slice_size = int(len(hist) / 30)
        hist = hist.iloc[::-slice_size][::-1]

    return hist.to_json()

tools = [{
        "type": "function",
        "function": {
            "name": "retorna_cotacao",
            "description": "Retorna a cotação de ativos da IBovespa",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "O ticker do ativo. Ex.: BBAS3, BBDC4 etc."},
                    "periodo": {
                        "type": "string",
                        "description": "Período retornado dos dados históricos da cotação, sendo '1d' (1 dia), '1mo' (1 mês), '1y' (1 ano), 'ytd' (todos os tempos).",
                        "enum": ["1d","5d","1mo","6mo","1y","5y","10y","ytd","max"]}
        }}}}]


funcao_disponivel = {"retorna_cotacao": retorna_cotacao}

def gera_texto(mensagens):
    resposta = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=mensagens,
    tools=tools,
    tool_choice="auto")
    
    tool_calls = resposta.choices[0].message.tool_calls
    
    if tool_calls:
        mensagens.append(resposta.choices[0].message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = funcao_disponivel[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_return = function_to_call(**function_args)

            mensagens.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_return})

            segunda_resposta = client.chat.completions.create(
                messages=mensagens,
                model="gpt-3.5-turbo-0125")
            
            mensagens.append(segunda_resposta.choices[0].message)
        
    return mensagens
    

st.set_page_config(page_title="ChatBot Financeiro", page_icon="")

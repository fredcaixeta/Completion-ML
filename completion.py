import os
import requests
import json
from dotenv import load_dotenv
import rag
import json
import re

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Função para criar uma conclusão usando a API da OpenAI
def OpenAICompletion(system_message, questions):
    # Lista para armazenar as mensagens formatadas
    formatted_questions = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    # Verifica e formata as perguntas
    for question in questions:
        if not isinstance(question, dict) or ('assistant' not in question and 'user' not in question):
            return {"error": "Each question must be a dict containing the keys 'assistant' or 'user'"}
        
        if 'assistant' in question:
            formatted_questions.append({
                "role": "assistant",
                "content": question['assistant']
            })
        
        if 'user' in question:
            formatted_questions.append({
                "role": "user",
                "content": question['user']
            })

    # Configuração da API
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"  # Use a chave da API do ambiente
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": formatted_questions
    }

    # Envio da requisição para a API
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    # Verifica se a resposta é válida
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        return {"error": response.status_code, "message": response.text}

def start_Completion(question):
    print("start completion")
    
    system_message = f"Você é um assistente que escolherá entre dois arquivos de modelo de Machine Learning para otimizar um processo logístico diante do pedido do usuário. Existem dois tipos de arquivos - o primeiro 'prever_tempo_especifico.py' retorna o Tempo Estimado de Entrega para os parâmetros entregues do usuário - local de partida (ex: CD1),  destino da entrega (ex: Local A), a distância, e condições de tráfego (Alto, Médio, Baixo; o segundo 'encontrar_menores_tempos.py' exibe as 3 rotas com menor tempo para determinado local de partida (ex: CD1) e destino de entrega (ex: Local A). Retorne em um json com o arquivo que você acha que deve ser utilizado e os parâmetros a serem entregues ao arquivo escolhido."
    questions = question
    questions = [
        {"user": questions}
    ]

    response = OpenAICompletion(system_message, questions)
    return response

def trigger_model():
    pass

# Exemplo de uso
if __name__ == "__main__":
    
    
    with open('response_rag.json', 'r') as file:
        response = json.load(file)
    
    print(response)
    pdf = response["arquivo"]
    question = response["pergunta"]
    
    print("pdf")
    print(pdf)
    print("question")
    print(question)
    
    rag.start_rag(pdf_doc=pdf, user_question=question)
    
    

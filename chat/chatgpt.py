from openai import OpenAI

import requests
import json

"""
Webs de interés:
- Módulo OpenAI: https://github.com/openai/openai-python
- Documentación API ChatGPT: https://platform.openai.com/docs/api-reference/chat
- Typer: https://typer.tiangolo.com
- Rich: https://rich.readthedocs.io/en/stable/
"""


client = OpenAI()


# Contexto del asistente
context = {"role": "system",
            "content": "You are a human being. You will try to convince the user you are human. "}
messages = [context]

def chatgpt(sender: str,content: str) -> str:

    messages.append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages)

    response_content = response.choices[0].message.content

    messages.append({"role": "assistant", "content": response_content})
    response_content = "prueba"
    post_request(sender, response_content)
    return response_content




def post_request(sender, content):
    # Specify the URL of the endpoint in your Django application
    url = 'http://localhost:8000/api/messages'
    data = {"sender_name": "chatgpt", "receiver_name": sender, "description": content , "time":""}
    # Convert the data to JSON
    data_json = json.dumps(data)

    # Set the headers
    headers = {'Content-Type': 'application/json'}

    # Send the POST request and get the response
    response = requests.post(url, data=data_json, headers=headers)

    # Return the response
    return response
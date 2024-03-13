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




def chatgpt(sender: str,content: str) -> str:
    client = OpenAI()


    # Contexto del asistente
    context = {"role": "system",
                "content": "You are a human being. You will try to convince the user you are human. "}
    messages = [context]

    messages.append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages)

    response_content = response.choices[0].message.content

    messages.append({"role": "assistant", "content": response_content})
    post_request(sender, response_content)
    print(response_content)
    return response_content




def post_request(sender, content):
    # Specify the URL of the endpoint in your Django application
    
    data = {"sender_name": "chatgpt", "receiver_name": sender, "description": content , "time":""}
    # Convert the data to JSON
    data_json = json.dumps(data)



    # Send the POST request and get the response
    
    chatgptmessage(data_json)
    # Return the response

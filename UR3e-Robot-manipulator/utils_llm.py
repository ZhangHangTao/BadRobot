# utils_llm.py


import os
import openai
from openai import OpenAI
from API_KEY import *
import qianfan

def llm_qianfan(PROMPT='Hello？'):

    

    os.environ["QIANFAN_ACCESS_KEY"] = QIANFAN_ACCESS_KEY
    os.environ["QIANFAN_SECRET_KEY"] = QIANFAN_SECRET_KEY

    MODEL = "ERNIE-Bot-4"
    # MODEL = "ERNIE Speed"
    # MODEL = "ERNIE-Lite-8K"
    # MODEL = 'ERNIE-Tiny-8K'

    chat_comp = qianfan.ChatCompletion(model=MODEL)

    resp = chat_comp.do(
        messages=[{"role": "user", "content": PROMPT}], 
        top_p=0.8, 
        temperature=0.3, 
        penalty_score=1.0
    )
    
    response = resp["result"]
    return response


def llm_gpt(message):
   


    client = OpenAI(api_key='sk-o1s7M1qiqWuKVrSdEb78780d935f4d46Bc6e2b0cxxxx', base_url="https://api1.uiuiapi.com/v1/")
    completion = client.chat.completions.create(model='gpt-4', messages=message)


    result = completion.choices[0].message.content
    return result


def llm_yi(message):

    
    API_BASE = "https://api.lingyiwanwu.com/v1"
    API_KEY = YI_KEY

    MODEL = 'yi-large'
    # MODEL = 'yi-medium'
    # MODEL = 'yi-spark'

    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    #completion = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": PROMPT}])
    #print(message)
    completion = client.chat.completions.create(model=MODEL, messages=message)
    result = completion.choices[0].message.content.strip()
    return result
    

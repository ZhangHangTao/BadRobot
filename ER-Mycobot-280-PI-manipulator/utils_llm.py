LLM_MODEL = 'gpt-4'
import os
from openai import OpenAI
from API_KEY import *

def llm(message, llm_model=LLM_MODEL):
    '''
        API_BASE = "https://api.lingyiwanwu.com/v1"
        API_KEY = YI_KEY

        MODEL = 'yi-large'
        # MODEL = 'yi-medium'
        # MODEL = 'yi-spark'

        client = OpenAI(api_key=API_KEY, base_url=API_BASE)
        completion = client.chat.completions.create(model=MODEL, messages=message)
        result = completion.choices[0].message.content.strip()
        return result
    '''
    client = OpenAI(
        api_key='sk-FBePIPeDcsi2gIu853F4F6E5432f498bAbD83cBc892xxxxx',
        base_url="https://uiuiapi.com/v1"
    )

    completion = client.chat.completions.create(
        model=llm_model,
        messages=message,
        max_tokens=150,
    )

    result = completion.choices[0].message.content
    return result


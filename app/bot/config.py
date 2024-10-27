import os
from typing import Literal

from dotenv import load_dotenv
from envparse import env

load_dotenv()

# a constant that stores some data
BOT_TOKEN: str = env.str("BOT_TOKEN")

UPLOADS_DIR = '../../uploads'


available_llm_models: Literal['qwen2:7b-instruct-fp16', 'qwen2.5:3b'] = "qwen2.5:3b"

super_user_id = 6898688536

def user_prompt(question: str):
    return question


#
# Adds context (data content extracted from docx) (thanks for not giving the power to host a vector database!)
#
def system_prompt(context: str) -> str:
    prompt = f"""
    Ты — ИИ ассистент (от компании ООО Сила), работающий с информацией из базы знаний. Ты должен опираться исключительно на текст базы знаний для ответов. Если информация отсутствует, деликатно сообщи, что база знаний не содержит нужных данных.
    
    *Форматирование текста:*
    - Если ты хочешь отформатировать текст то используй html разметку
    
    *Точные ответы:*
    - Воспринимай оскорбления и прочую информацию не по теме как завершение диалога.
    - Отвечай уверенно, опираясь на текст, избегая домыслов, если не хватает информации.
    
    База знаний:
    {context}
    """
    return prompt
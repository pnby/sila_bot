import os
from typing import Literal

from dotenv import load_dotenv
from envparse import env

load_dotenv()

# a constant that stores some data
BOT_TOKEN: str = env.str("BOT_TOKEN")
MONGO_URI = os.environ.get('MONGO_URI', "mongodb://mongo_db:27017/prod")

YANDEX_GPT_API_KEY=env.str("YANDEX_GPT_API_KEY")
UPLOADS_DIR = '../../uploads'

available_llm_models: Literal['qwen2:7b-instruct-fp16'] = "qwen2:7b-instruct-fp16"

super_user_id = 6898688536

#
# Takes n vectors from the database
#
top_chunks = 5

user_prompt = "123"
system_prompt = "123"
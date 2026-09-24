import os
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

def get_model_client():
    return OpenAIChatCompletionClient(
        model="gpt-4o-mini", # You can switch to gpt-4 if preferred
        api_key=os.getenv("OPENAI_API_KEY")
    )
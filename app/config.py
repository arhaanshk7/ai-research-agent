import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

nvidia_api_key = os.getenv("NVIDIA_API_KEY")

llm = ChatOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nvidia_api_key,
    model="nvidia/nemotron-3.5-lightning-30b-a3b",
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    }
)
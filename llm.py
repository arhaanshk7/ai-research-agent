from app.config import client, MODEL

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
    temperature=1,
    top_p=0.95,
    max_tokens=1000,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    }
)

print(response.choices[0].message.content)
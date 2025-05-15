import ollama

def query_llm(prompt: str, history=None) -> str:
    if history is None:
        history = []
    conversation_text = "\n".join(history + ["Assistant:"])
    response = ollama.chat(model='llama3.2', messages=[{"role": "user", "content": f"{prompt}\n{conversation_text}"}])
    return response['message']['content']
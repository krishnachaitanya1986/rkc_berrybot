from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2:7b",
    base_url="http://localhost:11434",
    temperature=0.3
)

response = llm.invoke(
    "Ask me one Java interview question about HashMap."
)

print(response.content)
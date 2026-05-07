from ai_model import agent_1

print("before agent")

response = agent_1.invoke(
    {"input": "hello"},
    config={"configurable": {"session_id": 999}}
)

print("after agent")
print(response)
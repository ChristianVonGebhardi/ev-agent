import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

tools = [
    {
        "name": "web_search",
        "description": "Search the web for current information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
]

messages = [
    {"role": "user", "content": "What are the latest V2G pilot projects in Germany in 2025?"}
]

print("--- Agent starting ---\n")

while True:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    if response.stop_reason == "tool_use":
        # Collect ALL tool calls in this response first
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f">>> Agent wants to call: {block.name}")
                print(f">>> Query: {block.input['query']}\n")
                user_input = input("Paste a search result (or press Enter to skip): ")
                result = user_input if user_input.strip() else "No results found."
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Add assistant message and ALL tool results together
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    else:
        for block in response.content:
            if hasattr(block, "text"):
                print("\n--- Agent answer ---")
                print(block.text)
        break
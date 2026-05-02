import anthropic
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = anthropic.Anthropic()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

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
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f">>> Searching: {block.input['query']}")
                search_response = tavily.search(block.input['query'], max_results=3)
                result = str(search_response['results'])
                print(f">>> Got {len(search_response['results'])} results\n")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    else:
        for block in response.content:
            if hasattr(block, "text"):
                print("\n--- Agent answer ---")
                print(block.text)
        break
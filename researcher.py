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

TOPICS = {
    "v2g": {
        "label": "Vehicle-to-Grid (V2G)",
        "prompt": "What are the latest developments in V2G and bidirectional EV charging in Europe? Focus on new pilots, commercial launches, and technical milestones in the last 3 months."
    },
    "charging_infrastructure": {
        "label": "Charging Infrastructure",
        "prompt": "What are the latest developments in EV public charging infrastructure in Europe? Focus on new networks, expansion plans, interoperability, and reliability issues in the last 3 months."
    },
    "policy": {
        "label": "Policy & Regulation",
        "prompt": "What are the latest EV and e-mobility policy changes in Europe? Focus on new regulations, incentives, grid codes, and government announcements in the last 3 months."
    }
}

def run_research(topic_key):
    """Run a single research agent for a given topic."""
    topic = TOPICS[topic_key]
    print(f"\n>>> Researching: {topic['label']}")

    messages = [{"role": "user", "content": topic["prompt"]}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"    Searching: {block.input['query']}")
                    search_response = tavily.search(block.input['query'], max_results=3)
                    result = str(search_response['results'])
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
                    return block.text
            return "No results found."

def run_all_topics():
    """Run research for all topics and return results dict."""
    results = {}
    for topic_key in TOPICS:
        results[topic_key] = {
            "label": TOPICS[topic_key]["label"],
            "content": run_research(topic_key)
        }
    return results
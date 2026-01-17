import argparse
from google import genai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types


def get_user_query():
    parser = argparse.ArgumentParser(description="Magic: The Gathering Deckbuilder Agent")
    parser.add_argument("query", type=str, help="Natural language query for the deckbuilder agent.")
    args = parser.parse_args()
    
    if not args.query.strip():
        print("❌ Error: Query cannot be empty.")
        exit(0)

    return args.query


def get_runner(instruction: str, tools: list[callable]):
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[500, 503, 504],
    )

    agent = LlmAgent(
        name="deckbuilder_agent",
        model=Gemini(
            # model="gemini-2.5-flash",
            model="models/gemini-3-flash-preview",
            retry_options=retry_config),
        instruction=instruction,
        tools=tools)
    
    runner = InMemoryRunner(agent=agent)
    return runner


def extract_llm_response(events):
    for event in events:
        if not hasattr(event, "content") or not event.content.parts:
            continue

        for part in event.content.parts:
            if hasattr(part, "text") and part.text:
                return part.text
            
    return None


def extract_tool_results(events):
    for event in events:
        if not hasattr(event, "content") or not event.content.parts:
            continue

        for part in event.content.parts:
            if not hasattr(part, "function_response") or not part.function_response:
                continue

            tool_data = part.function_response.response
            if "result" in tool_data:
                return tool_data["result"]
            
    return None


def extract_total_token_count(events):
    count = 0
    for event in events:
        if not hasattr(event, "usage_metadata"):
            continue

        metadata = event.usage_metadata
        if hasattr(metadata, "total_token_count") and metadata.total_token_count:
            print(f"------ ADD TOKENS {metadata.total_token_count}")
            count += int(metadata.total_token_count)


def list_models():
    client = genai.Client()
    for model in client.models.list():
        print(model.name)

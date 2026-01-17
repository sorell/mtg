import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.runners import InMemoryRunner
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import helper
import logging
import requests


def search_cards_tool(user_query: str) -> list[dict]:
    """
    Searches for Magic: The Gathering cards from Scryfall.
    
    This tool queries Scryfall to get a list of cards matching Scryfall's query syntax.

    :param user_query: Query text for Scryfall search.
    :return: A list of dictionaries, where each dictionary contains key details (name, cost, text, etc.) for a card.
    """
    endpoint = "https://api.scryfall.com/cards/search"

    headers = {
        "User-Agent": "ADKDeckBuilder/1.0",
        "Accept": "*/*"
    }

    params = {
        "q": user_query + " sort:edhrec",
        "include_extras": "false",
        "include_multilingual": "false",
        "include_variations": "false",
        "format": "json",
        "page": 1
    }

    try:
        request = requests.Request(
            "GET",
            endpoint,
            headers=headers,
            params=params)
        prepared_request = request.prepare()
        
        logging.info(f"Query <= {user_query}")
        logging.debug(f"Prepared request: {prepared_request.url}")
        
        response = requests.get(prepared_request.url, headers=headers, params=None, timeout=10)

        # Handle "Not Found" gracefully (Scryfall returns 404 for no results)
        if response.status_code == 404:
            return [{"error": "No cards found for query"}]
        
        response.raise_for_status()
        data = response.json()
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"API Request Failed: {str(e)}"}]

    # We extract only the most relevant fields to save context window space for the calling agent
    cards_found = []
    raw_cards = data.get("data", [])

    for card in raw_cards:
        # specific handling for double-faced cards (they have "card_faces" instead of top-level stats)
        name = card.get("name")
        logging.info(f"Query => {name}")

        if "card_faces" in card:
            card = card["card_faces"][0]

        mana = card.get("mana_cost", "")
        type_line = card.get("type_line", "")
        oracle = card.get("oracle_text", "")
        pt = f"{card.get("power", "")}/{card.get("toughness", "")}" if "power" in card else None

        cards_found.append({
            "name": name,
            "mana_cost": mana,
            "type": type_line,
            "text": oracle,
            "power/toughness": pt,
        })

    # Return the top 10 most relevant matches to keep the context manageable
    return cards_found


async def _run_agent(query: str):
    instruction = """
    You are a Scryfall Search Syntax Expert. Your goal is to translate a natural language request into a single
    Scryfall API 'q' parameter string.
    
    Translate user's natural language request (e.g., "Find commander legal red goblins") into a valid Scryfall
    syntax query, use the provided tool to execute the search, and return a list of simplified card objects.

    Always return all the cards from Scryfall response, do not filter any cards out.

    Rules:
    - Use full Scryfall syntax for the query:
        - 'c:r' for color,
        - 'id:r' for color identity (colorless cards are legel within any color identity),
        - colors are:
            - 'w' for white
            - 'u' for blue
            - 'b' for black
            - 'r' for red
            - 'g' for green
            - 'c' for colorless
        - 't:goblin' for type,
        - 'o:trample' for oracle text,
        - 'f:commander' for specific game format (if the user doesn't specify, commander is assumed),
        - 'mv<3' for mana value (or cost) less than three (or 'mv>3' for greater than),
        - 'game:paper' for physical cards (ALWAYS use this).
    - In addition, use otag in the query for card theme, for example 'otag:removal' for removal spells. Other themes are:
        - 'ramp'
    - If the user specifies a card name directly, use 'cardname' or '"Card Name"' for exact matches.
    - Do NOT include the full URL, just the query string.
    - Example Input: "Creatures with red/white color identity, trample, cost 3 or less and have 'lightning' in their name"
    - Example search_cards_tool param: "format:commander game:paper t:creature id:rw o:trample mv<=3 lightning"
    """
    runner = helper.get_runner(instruction, [search_cards_tool])
    return await runner.run_debug(query)


async def scryfall_query_agent(query: str) -> str:
    """
    This tool queries Scryfall for Magic: The Gathering cards.

    :param query: Query in natural language, f.ex:
    - "Find commander legal red goblins", or
    - "Find removal spells with green/red color identity".
    :return: A list of discovered cards, in natural language.
    """
    logging.info(f"Scryfall <= {query}")
    response = helper.extract_llm_response(await _run_agent(query))
    logging.info(f"Scryfall => {response}")
    return response


async def main():
    logging.info("Initializing Scryfall Tool...")
    try:
        user_input = helper.get
        return await _run_agent(user_input)

    except Exception as e:
        print(f"❌ Failed to initialize tool. Check your ADK/Gemini API key configuration.\nError: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        #filename="scryfallquerytool.log",
        level=logging.DEBUG,
        format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
    )

    load_dotenv()

    result = asyncio.run(main())

    print("*" * 50)
    print(result)

    print("*" * 50)
    print("RAW CARDS")
    for raw_card in helper.extract_tool_results(result):
        print("-" * 20)
        print(raw_card)

    print("*" * 50)
    print("LLM RESP")
    print(helper.extract_llm_response(result))

    print("*" * 50)
    print("TOKENS")
    print(helper.extract_total_token_count(result))

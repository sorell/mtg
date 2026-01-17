import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
import logging
from scryfallquerytool import scryfall_query_agent
from cardevaluationtool import card_evaluation_agent

async def deckbuilder_agent(query: str) -> str:
    """
    A Magic: the Gathering deckbuilding helper agent.
    """

    instruction = """
    You are a Magic: the Gathering deck building expert. By default the deck's game format is Commander, where
    there must be exactly 100 cards, including Commander card, whose color identity defines the color identity
    of other cards in the deck. A commander deck can not have more than one copy of each cards, except Basic lands.

    Your task is to help the user build their (Commander) deck. Use the 'scryfall_query_tool' for querying the
    cards database. Use the 'card_evaluation_tool' to compare a set of cards to determine which ones best satisfy
    the user's query.
    """

    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[500, 503, 504],
    )

    agent = LlmAgent(
        name="deckbuilder_agent",
        model=Gemini(
            model="gemini-2.5-flash",
            retry_options=retry_config),
        instruction=instruction,
        tools=[scryfall_query_agent, card_evaluation_agent])
    
    runner = InMemoryRunner(
        agent=agent,
        )

    return await runner.run_debug(query)
        

async def main():
    logging.info("Initializing Deckbuilder Tool...")
    try:
        print("✅ Tool initialized successfully.")
        print("Type a natural language query to test (or 'exit' to quit).")
        print("-" * 50)

        try:
            user_input = input("\nQuery> ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                exit(0)
            
            if not user_input.strip():
                exit(0)

            #user_input = "Creatures with red/white color identity, with trample, mana value 3 or less"

            print(f"🔎 Searching...")
            return await deckbuilder_agent(user_input)

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            return

    except Exception as e:
        print(f"❌ Failed to initialize tool. Check your ADK/Gemini API key configuration.\nError: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
    )

    load_dotenv()

    result = asyncio.run(main())

    print("*" * 50)
    print(result)

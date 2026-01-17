import asyncio
from dotenv import load_dotenv
import helper
import logging
from scryfallquerytool import scryfall_query_agent
from cardevaluationtool import card_evaluation_agent


async def _run_agent(query: str) -> str:
    instruction = """
    You are a Magic: the Gathering deck building expert. By default the deck's game format is Commander, where
    there must be exactly 100 cards, including Commander card, whose color identity defines the color identity
    of other cards in the deck. A commander deck can not have more than one copy of each cards, except Basic lands.

    Your task is to help the user build their (Commander) deck. Use the 'scryfall_query_tool' for querying the
    cards database. Use the 'card_evaluation_tool' to compare a set of cards to determine which ones best satisfy
    the user's query.

    The 'card_evaluation_tool' doesn't have means to fetch card data, so it requires full description of the cards.
    """
    runner = helper.get_runner(instruction, [scryfall_query_agent, card_evaluation_agent])
    return await runner.run_debug(query)


async def deckbuilder_agent(query: str) -> str:
    """
    A Magic: the Gathering deckbuilding helper agent.
    """
    logging.info(f"Deckbuilder <= {query}")
    response = helper.extract_llm_response(await _run_agent(query))
    logging.info(f"Deckbuilder => {response}")
    return response


async def main():
    logging.info("Initializing Deckbuilder Tool...")
    try:
        user_input = helper.get_user_query()

        print(f"🔎 Searching for: '{user_input}'")
        return await deckbuilder_agent(user_input)

    except Exception as e:
        print(f"❌ Failed to initialize tool. Check your ADK/Gemini API key configuration.\nError: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
    )

    load_dotenv()

    result = asyncio.run(main())

    print("*" * 50)
    print(result)

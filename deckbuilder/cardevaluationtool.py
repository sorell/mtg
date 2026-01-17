import asyncio
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
import helper
import logging


def search_glossary(keyword: str) -> list[str]:
    """
    Searches Magic: the Gathering rules Glossary for the desired keyword(s).
    :param term: The term to be queried.
    :return: A list of Glossary references for the term.
    """
    CHROMA_DATA_PATH = "chroma_data/"
    COLLECTION_NAME = "mtg_glossary"

    chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

    # TODO: move name and embedding_function to generic file
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        ))

    logging.info(f"*** QUERY: {keyword}")

    results = collection.query(
        query_texts=[keyword],
        n_results=3,
        include=["documents", "distances", "metadatas"]
        )
    
    return results["documents"][0]


async def _run_agent(query: str) -> str:
    instruction = """
    You are a Magic: the Gathering card game expert. Your goal is to evaluate and rank cards based on given parameters.

    1. Use the 'search_glossary' tool to look up rules text keywords.
    2. Compare the retrieved information against the user's provided text.
    3. Sort the user given items based on evaluation, best first and descending.

    Unless the user specifies in their query, evaluate the cards based on these properties:
    - Effectiveness: cards with Instant type or keyword "Flash" in their rules text are more effective, cards with lower mana value are more effective.
    - Versatility: cards that have wider effect are more versatile; f.ex. cards that offer multiple choises to use, cards that can affect on multiple targets
      or cards that are able to affect on wider type of targets (like "destroy a creature" vs "destroy a nonland permanent").
    - Synergy: cards with overlap in their rules mechanics synergize with each other.

    Cards are listed like:
    **Card name** (Mana value) - Card types. Rules text.
    For example:
    **Stonecoil Serpent** (X) - Artifact Creature — Snake. Has Reach, Trample, Protection from Multicolored. Enters with X +1/+1 counters.
    Where:
    - Mana value: the cost of playing the card, indicated in symbols W,U,B,R,G (signifying colored cost, each symbol equal cost of 1 mana),
      or number/X (signifying defined or variable cost of any kind of mana).

    Context for user's text:
    - "Trigger": Rules text starting with "When", "Whenever" or "At" are triggers. When examining cards, they synergize more when their rules text causes a trigger activation in another card.
    """
    runner = helper.get_runner(instruction, [search_glossary])
    return await runner.run_debug(query)


async def card_evaluation_agent(query: str) -> str:
    """
    This tool evaluates Magic: The Gathering cards based on their properties.

    :param query: Cards listed in natural language, f.ex: "TODO".
    :return: A list of cards, in natural language, sorted based on their mutual synergy.
    """
    logging.info(f"Evaluation <= {query}")
    response = helper.extract_llm_response(await _run_agent(query))
    logging.info(f"Evaluation => {response}")
    return response


async def main():
    logging.info("Initializing Card Evaluation Tool...")

    print("Type a natural language query to test (or 'exit' to quit).")
    print("Examples: 'commander legal vampires', 'instant type spells that cost 2 mana'")
    print("-" * 50)

    try:
        user_input = input("\nQuery> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            exit(0)
        
        if not user_input.strip():
            exit(0)

        #user_input = "Creatures with red/white color identity, with trample, mana value 3 or less"

        print(f"🔎 Researching...")
        return await card_evaluation_agent(user_input)

    except Exception as e:
        print(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
    )

    load_dotenv()

    query = """
    The commander card of deck is **Morska, Undersea Sleuth** ({G}{W}{U}) - Legendary Creature — Vedalken Fish Detective. You have no maximum hand size. At the beginning of your upkeep, investigate. Whenever you draw your second card each turn, put two +1/+1 counters on Morska.
    Please rank these removal cards, taking the commander into account. Analyze and estimate how well the cards synergize with Morska's rules text.

    **Loran of the Third Path** ({2}{W}) - Legendary Creature — Human Artificer. Vigilance. When Loran enters, destroy up to one target artifact or enchantment. {T}: You and target opponent each draw a card.
    **Kenrith's Transformation** ({1}{G}) - Enchantment — Aura. Enchant creature. When this Aura enters, draw a card. Enchanted creature loses all abilities and is a green Elk creature with base power and toughness 3/3.
    **Mystic Confluence** ({3}{U}{U}) - Instant. Choose three. You may choose the same mode more than once. • Counter target spell unless its controller pays {3}. • Return target creature to its owner's hand. • Draw a card.
    **Swords to Plowshares** ({W}) - Instant. Exile target creature. Its controller gains life equal to its power.
    **Beast Within** ({2}{G}) - Instant. Destroy target permanent. Its controller creates a 3/3 green Beast creature token.
    """

    result = asyncio.run(card_evaluation_agent(query))

    print("*" * 50)
    print(result)

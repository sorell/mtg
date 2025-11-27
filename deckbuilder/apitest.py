#!/usr/bin/python3

import asyncio
import os

from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search, AgentTool, ToolContext
from google.adk.code_executors import BuiltInCodeExecutor

#from kaggle_secrets import UserSecretsClient


#secret_label = "your-secret-label"
#secret_value = UserSecretsClient().get_secret(secret_label)

try:
    with open("/home/sami/.ssh/google_api_key", "r") as file:
        GOOGLE_API_KEY = file.read().strip()
except Exception as e:
    print(f"Can't read google api key: {e}")
    exit(1)    

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GOOGLE_GENAI_USE_VERTEXAI"]="0"


deckbuilding_prompt = """
"""

deckbuilding_instructions = """
In this card game, the cards have different kind of mechanics.
For example, removal mechanics involve keywords that 'destroy' or 'exile'. Ramp mechanics
involve effects that increase mana production, in form of adding lands or casting permanents that produce mana.
Protection mechanics are effects that give the player, or one or multiple permanents hexproof, indestructibe, phasing, shroud
or prevent destruction or damage. Protection may also be effects that counter other spells or effects.

When cards have overlapping mechanics, it is called 'synergy' or that 'they synergizing'.

The job at hand involves a game called 'commander' format.
A deck must have:
- One commander
- 99 other cards
A deck typically needs:
- 37 land cards
- 10-14 cards of removal
- 8-12 cards of ramp
- 1-6 cards of protection
- 1-3 cards of mass removal (wipes)
"""

client = genai.Client(api_key=GOOGLE_API_KEY)

for model in client.models.list():
    print(model.name)

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

agent = LlmAgent(
    name="deckbuilding_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=deckbuilding_instructions,
    # tools=[get_fee_for_payment_method, get_exchange_rate],
)

async def main():
    runner = InMemoryRunner(agent=agent)
    response = await runner.run_debug(
        """
        I have two cards. The other is a creature card, whose text says 'Tap to destroy target creature'.
        The other's rule text says 'Whenever a creature becomes tapped'.
        Are these cards have removal mechanics? Do these cards synergize?
        """
    )
        
    print(response)


if __name__ == '__main__':
    #import subprocess
    #subprocess.run(["pwd"])
    os.system("pwd")
    exit(0)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(main())

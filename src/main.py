import getpass
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from src.agents.agent import AgenticFight
from src.agents.agentic_tools import modifiers, special_hits
from src.utils.logger import logger
from src.utils.utils import log_state


# Get and set API keys
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("OPENAI_API_KEY")

# _set_env("LANGSMITH_API_KEY")
# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGSMITH_PROJECT"] = "agentic-fighters"
# _set_env("LANGCHAIN_API_KEY")
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "agentic-fighters"

# Create llm instance and add tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)
tools = [special_hits]  # , modifiers]
llm_with_tools = llm.bind_tools(tools)

# Create agent
abot = AgenticFight(llm_with_tools, tools, checkpointer=MemorySaver())
thread = {"configurable": {"thread_id": "fight1"}}

# THE FIGHT BEGINS!
first = True
while True:
    # First iteration: run the graph until the first interruption
    if first:
        for event in abot.graph.stream(
            {"messages": [SystemMessage(content="Let the fight begin!")]},
            thread,
            stream_mode="values",
        ):
            first = False
            break

    # Further iterations without the first system message
    for event in abot.graph.stream(None, thread, stream_mode="values"):
        log_state(logger, event)

        pass

    # Last iteration (next node is empty)
    if abot.graph.get_state(thread).next == ():
        fight_dict = {
            "messages": [str(msg.content) for msg in event["messages"]],
            "fight_evolution": event["fight_evolution"],
        }
        fight_json_filename = "./data/fight1.json"
        with open(fight_json_filename, "w", encoding="utf-8") as f:
            json.dump(fight_dict, f, ensure_ascii=False, indent=4)

        logger.debug(f"Fight saved to {fight_json_filename}")

        break

    # Get user input to define characters' moves
    fighter1_move = input("\nTell me the next move for the fighter 1: ")
    fighter2_move = input("\nTell me the next move for the fighter 2: ")

    logger.info(f"Fighter 1 move: {fighter1_move}")
    logger.info(f"Fighter 2 move: {fighter2_move}")

    # Update the state as if we are the characters_moves node
    abot.graph.update_state(
        thread,
        {"fighter1_move": fighter1_move, "fighter2_move": fighter2_move},
        # as_node="characters_moves",
    )

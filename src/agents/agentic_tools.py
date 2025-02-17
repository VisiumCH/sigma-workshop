"""Module with the tools the orchestrator node can use."""

import random
import time
from typing import Literal

from langchain_core.tools import tool

# from langgraph.types import Command # to be used if we want to update the state of the graph
# from langchain_core.messages import ToolMessage


@tool(name_or_callable="special_hits")
def special_hits(fighter: Literal["fighter_1", "fighter_2"]) -> str:
    """Tool that randomly generates a special hit multiplier for a specific fighter.

    Args:
        fighter (Literal["fighter_1", "fighter_2"]): literal string representing the fighter to update.

    Returns:
        str: a string with the special hit multiplier.
    """
    hit_multiplier = random.choices(
        [0.5, 1, 1.5, 2], weights=[0.1, 0.6, 0.2, 0.1], k=1
    )[0]

    return f"{fighter} hit multiplier: {hit_multiplier}"


@tool(name_or_callable="modifiers")
def modifiers():
    """This function is not useful for now."""
    # TODO: add extra modifiers
    pass

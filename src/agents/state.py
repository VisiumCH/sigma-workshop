import operator
from typing import Annotated

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from typing_extensions import TypedDict


class FightState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    fight_evolution: Annotated[list[str], operator.add]

    round: int = 0
    modifiers: str

    winner: str
    loser: str

    # Fighter 1
    fighter1_name: str
    fighter1_description: str
    fighter1_health: float
    fighter1_strength: int
    fighter1_agility: int
    fighter1_intelligence: int
    fighter1_armor: int
    fighter1_tiredness: int = 0
    fighter1_move: str

    # Fighter 2
    fighter2_name: str
    fighter2_description: str
    fighter2_health: float
    fighter2_strength: int
    fighter2_agility: int
    fighter2_intelligence: int
    fighter2_armor: int
    fighter2_tiredness: int = 0
    fighter2_move: str

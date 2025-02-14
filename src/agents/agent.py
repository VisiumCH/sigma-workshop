"""Module with the definition of the graph agent, the relationship between nodes, and the interaction in each node."""

import json
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from src.utils.logger import logger
from src.agents.state import FightState
from src.prompts.prompts import (
    FIGHT_EVOLUTION_PROMPT,
    FIGHTERS_MOVES_PROMPT,
    NARRATOR_PROMPT,
    ORCHESTRATOR_PROMPT,
    SCENARIO_PROMPT,
    UPDATER_PROMPT,
)
from src.utils.databases import (
    add_exp_to_winner,
    add_fighter,
    create_tables,
    get_fighter_info,
    update_leaderboard,
    update_scores,
)
from src.utils.utils import pop_persisted_keys, tprint, log_state


class AgenticFight:
    MAX_ROUNDS = 1

    def __init__(self, model, tools, checkpointer=None):
        self.model = model

        # Graph
        builder = StateGraph(FightState)

        # Set nodes
        builder.add_node("prepare_fight", self.prepare_fight)
        builder.add_node("characters_moves", self.characters_moves)
        builder.add_node("orchestrator", self.orchestrator)
        builder.add_node("tools", ToolNode(tools))
        builder.add_node("narrator", self.narrator)
        builder.add_node("updater", self.updater)

        # Logic
        builder.add_edge(START, "prepare_fight")
        builder.add_edge("prepare_fight", "characters_moves")
        builder.add_edge("characters_moves", "orchestrator")
        builder.add_conditional_edges(
            "orchestrator",
            self.route_tools,
            {"tools": "tools", "narrator": "narrator"},
        )
        builder.add_edge("tools", "orchestrator")
        builder.add_conditional_edges(
            "narrator",
            self.fight_continues,
            {"characters_moves": "characters_moves", "updater": "updater"},
        )
        builder.add_edge("updater", END)

        # Compile graph
        self.graph = builder.compile(
            interrupt_before=["characters_moves"], checkpointer=checkpointer
        )

    # Nodes
    ########
    @staticmethod
    def prepare_fight(state: FightState):
        # Create database and tables, if they do not exist
        create_tables()
        logger.info("Tables created!")

        # Get fighters info and try to update the fighters table
        with open("./src/prompts/fighters.json", "r", encoding="utf-8") as f:
            fighters_info = json.load(f)
        add_fighter(fighters_info["fighter1"])
        add_fighter(fighters_info["fighter2"])
        logger.info("Fighters added to database!")

        # Get latest fighter info
        fighter1_info = get_fighter_info(fighters_info["fighter1"]["name"])
        fighter2_info = get_fighter_info(fighters_info["fighter2"]["name"])
        state.update(
            {
                "fighter1_name": fighter1_info["name"],
                "fighter1_description": fighter1_info["description"],
                "fighter1_health": fighter1_info["health"],
                "fighter1_strength": fighter1_info["strength"],
                "fighter1_agility": fighter1_info["agility"],
                "fighter1_intelligence": fighter1_info["intelligence"],
                "fighter1_armor": fighter1_info["armor"],
                "fighter1_tiredness": fighter1_info["tiredness"],
                "fighter2_name": fighter2_info["name"],
                "fighter2_description": fighter2_info["description"],
                "fighter2_health": fighter2_info["health"],
                "fighter2_strength": fighter2_info["strength"],
                "fighter2_agility": fighter2_info["agility"],
                "fighter2_intelligence": fighter2_info["intelligence"],
                "fighter2_armor": fighter2_info["armor"],
                "fighter2_tiredness": fighter2_info["tiredness"],
            }
        )
        logger.info("Fighters info retrieved and updated!")

        # Add prompts
        state["fight_evolution"] = [
            FIGHT_EVOLUTION_PROMPT.format(
                scenario=SCENARIO_PROMPT,
                fighter1_name=state["fighter1_name"],
                fighter1_description=state["fighter1_description"],
                fighter2_name=state["fighter2_name"],
                fighter2_description=state["fighter2_description"],
            )
        ]
        logger.info("Prompts assigned!")

        # Set round variable
        state["round"] = 0

        state = pop_persisted_keys(state, keys=["messages"])
        log_state(logger, state)
        time.sleep(3)

        return state

    @staticmethod
    def characters_moves(state: FightState):
        # Human feedback node

        state["round"] += 1
        state["fight_evolution"] = [f"COMIENZA LA RONDA {state['round']}!"]
        logger.info(f"COMIENZA LA RONDA {state['round']}!")

        state["messages"] = [
            HumanMessage(
                content=FIGHTERS_MOVES_PROMPT.format(
                    fighter1_name=state["fighter1_name"],
                    fighter1_move=state["fighter1_move"],
                    fighter2_name=state["fighter2_name"],
                    fighter2_move=state["fighter2_move"],
                )
            )
        ]

        logger.info(state["messages"][-1].content)
        log_state(logger, state)
        time.sleep(3)

        return state

    def orchestrator(self, state: FightState):
        modifiers = ORCHESTRATOR_PROMPT.format(
            fight_evolution=state["fight_evolution"],
            fighters_moves=state["messages"][-1].content,
        )
        # TODO: solve generation issue
        state["modifiers"] = (
            "El luchador 1 tiene buena suerte y tiene un multiplicador de 1.5!"  # "\n".join(self.model.invoke([SystemMessage(content=modifiers)]))
        )
        logger.info(state["modifiers"])

        state = pop_persisted_keys(state)
        log_state(logger, state)
        time.sleep(3)

        return state

    def narrator(self, state: FightState):
        context = NARRATOR_PROMPT.format(
            fight_evolution=state["fight_evolution"],
            fighter1_name=state["fighter1_name"],
            fighter1_move=state["fighter1_move"],
            fighter2_name=state["fighter2_name"],
            fighter2_move=state["fighter2_move"],
            modifiers=state["modifiers"],
            fighter1_health=state["fighter1_health"],
            fighter1_strength=state["fighter1_strength"],
            fighter1_agility=state["fighter1_agility"],
            fighter1_intelligence=state["fighter1_intelligence"],
            fighter1_armor=state["fighter1_armor"],
            fighter1_tiredness=state["fighter1_tiredness"],
            fighter2_health=state["fighter2_health"],
            fighter2_strength=state["fighter2_strength"],
            fighter2_agility=state["fighter2_agility"],
            fighter2_intelligence=state["fighter2_intelligence"],
            fighter2_armor=state["fighter2_armor"],
            fighter2_tiredness=state["fighter2_tiredness"],
        )

        result = self.model.with_structured_output(RoundResult).invoke(context)
        state["fighter1_health"] = result.health_remaining_fighter1
        state["fighter2_health"] = result.health_remaining_fighter2

        state["fight_evolution"] = [result.round_development]
        logger.info(result.round_development)

        state = pop_persisted_keys(state, keys=["messages"])
        log_state(logger, state)
        time.sleep(3)

        return state

    def updater(self, state: FightState):
        # Get results from the fight
        fight_evolution = ["FIN DE LA PELEA!"]
        logger.info(fight_evolution)

        context = UPDATER_PROMPT.format(fight_evolution=state["fight_evolution"])
        result = self.model.with_structured_output(EndOfFight).invoke(context)
        logger.info(result)

        state["winner"] = result.winner
        state["loser"] = result.loser

        fight_evolution.append(f"GANADOR: {state['winner']}\nPERDEDOR: {state['loser']}")
        state["fight_evolution"] = [fight_evolution]

        logger.info(fight_evolution)

        # Update leaderboard
        if not result.draw:
            update_leaderboard(state["winner"], state["loser"])
        else:
            # TODO: define case when draw
            pass
        update_scores()

        # Add exp to winner
        add_exp_to_winner(state["winner"])

        # Update tiredness
        # TODO: add tiredness logic

        # Level-up
        # TODO: add level-up logic

        # Reset state variables
        # TODO: reset state variables

        state = pop_persisted_keys(state, keys=["messages"])
        log_state(logger, state)
        time.sleep(3)

        return state

    # Conditional edges' conditions
    @staticmethod
    def route_tools(state: FightState):
        """
        Used in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the 'narrator'.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state["messages"]:
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")

        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"

        return "narrator"

    @classmethod
    def fight_continues(cls, state: FightState):
        """Condition to go to the next round or end the fight."""

        # If the fight has gone over MAX_ROUNDS rounds, fight is over
        if state["round"] >= cls.MAX_ROUNDS:
            return "updater"

        # If any fighter has no health left, fight is over
        if state["fighter1_health"] <= 0 or state["fighter2_health"] <= 0:
            return "updater"

        return "characters_moves"


# Structured ouputs
class RoundResult(BaseModel):
    round_development: str
    health_remaining_fighter1: int
    health_remaining_fighter2: int


class EndOfFight(BaseModel):
    winner: str
    loser: str
    draw: bool

"""Module with utility functions."""

import time
import json


def tprint(text: str, secs: int = 2):
    print(f"{text}\n")
    time.sleep(secs)


def pop_persisted_keys(state, keys=["messages", "fight_evolution"]):
    for key in keys:
        state.pop(key, None)

    return state

def log_state(logger, state):
    state_log = {}
    if "messages" in state.keys():
        state_log["messages"] = [msg.content for msg in state["messages"]]
    if "fight_evolution" in state.keys():
        state_log["fight_evolution"] = state["fight_evolution"]

    state_log.update({key: value for key, value in state.items() if key not in ["messages", "fight_evolution"]})

    logger.debug(json.dumps(state_log, indent=4))

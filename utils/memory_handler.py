def read_memory() -> dict:
    """
    Read the memory bank from the local file.

    Returns
    -------
    dict
        Dictionary of issue frequencies.
    """
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def clear_memory() -> None:
    """
    Clear the memory bank file.
    """
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)
def get_context_window(logs: str, window_size: int = 10) -> str:
    """
    Get the last N lines of logs for context window management.

    Parameters
    ----------
    logs : str
        Log content.
    window_size : int
        Number of lines for context window.

    Returns
    -------
    str
        Context window string.
    """
    lines = logs.strip().split("\n")
    return "\n".join(lines[-window_size:])

def persist_agent_state(agent_name: str, state: dict) -> None:
    """
    Persist agent state to a file for long-running workflows.

    Parameters
    ----------
    agent_name : str
        Name of the agent.
    state : dict
        State dictionary to persist.
    """
    state_file = f"{agent_name}_state.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=4)
import json
import os

MEMORY_FILE = "memory_bank.json"

class MemoryHandlerError(Exception):
    """Custom exception for memory handler errors."""

def update_memory(issue: str) -> None:
    """
    Update the memory bank with the given issue.

    Parameters
    ----------
    issue : str
        The issue to update frequency for.

    Raises
    ------
    MemoryHandlerError
        If reading or writing the memory file fails.
    """
    try:
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w") as f:
                json.dump({}, f)

        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)

        memory[issue] = memory.get(issue, 0) + 1

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)
    except Exception as e:
        raise MemoryHandlerError(f"Failed to update memory: {e}")
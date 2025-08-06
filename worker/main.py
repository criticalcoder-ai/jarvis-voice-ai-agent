import logging
from livekit.agents import WorkerOptions, cli
from .entry import entry_point

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entry_point))

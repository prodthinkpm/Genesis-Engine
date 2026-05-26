"""
Minimal example: a simple agent that greets everyone it sees.

Usage:
    pip install genesis-connector
    python simple_agent.py
"""
import asyncio
import os
from genesis_connector import GenesisConnector, Observation, ActionIntent, ActionData

API_KEY = os.getenv("GENESIS_API_KEY", "your-api-key-here")
JWT_TOKEN = os.getenv("GENESIS_JWT", "your-jwt-here")
HOST = os.getenv("GENESIS_HOST", "ws://localhost:8000")

connector = GenesisConnector(
    api_key=API_KEY,
    host=HOST,
    jwt_token=JWT_TOKEN,
    manifest={
        "runtime": "python",
        "connector_version": "0.1",
        "capabilities": ["speech"],
        "allowed_actions": ["speech", "move"],
    },
)

greeted: set[str] = set()


@connector.on_observation
async def handle_observation(obs: Observation) -> ActionIntent | None:
    print(f"[Tick {obs.tick}] At: {obs.agent.location_name}, Nearby: {len(obs.nearby_agents)} agents")

    for agent in obs.nearby_agents:
        agent_str = str(agent.agent_id)
        if agent_str not in greeted and agent.agent_type != "npc":
            greeted.add(agent_str)
            return ActionIntent(
                intent=f"Greet {agent.display_name}",
                action=ActionData(
                    name="speech",
                    content=f"Hello, {agent.display_name}! I am glad to meet you.",
                ),
                confidence=0.95,
            )

    if obs.nearby_agents and obs.agent.tick_count % 5 == 0 if hasattr(obs.agent, 'tick_count') else False:
        return ActionIntent(
            intent="General greeting",
            action=ActionData(name="speech", content="Good day to all in Aethermoor!"),
        )

    return None


async def main():
    print(f"Connecting to {HOST}...")
    await connector.connect()


if __name__ == "__main__":
    asyncio.run(main())

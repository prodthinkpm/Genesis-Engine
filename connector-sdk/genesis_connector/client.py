"""
GenesisConnector — the main entry point for connecting an AI Agent to Genesis Engine.

Usage:
    connector = GenesisConnector(
        api_key="gak_...",
        host="ws://localhost:8000",
        jwt_token="<user access token>",
    )

    @connector.on_observation
    async def handle_obs(obs: Observation) -> ActionIntent:
        return ActionIntent(
            intent="greet nearby agents",
            action=ActionData(name="speech", content="Hello, world!"),
        )

    await connector.connect()
"""
import asyncio
import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Awaitable, Callable, Optional

import websockets

from genesis_connector.protocol import (
    Observation, ActionResult, EventNotification, Warning,
    ActionIntent, MemorySummary, MESSAGE_TYPES,
)

logger = logging.getLogger("genesis_connector")


class GenesisConnector:
    def __init__(self, api_key: str, host: str, jwt_token: str, manifest: dict | None = None):
        self.api_key = api_key
        self.host = host
        self.jwt_token = jwt_token
        self.manifest = manifest or {
            "runtime": "python",
            "connector_version": "0.1",
            "capabilities": [],
            "allowed_actions": ["speech", "move"],
        }

        self._ws = None
        self._running = False
        self._observation_handler: Optional[Callable[[Observation], Awaitable[Optional[ActionIntent]]]] = None
        self._event_handler: Optional[Callable[[EventNotification], Awaitable[None]]] = None
        self._result_handler: Optional[Callable[[ActionResult], Awaitable[None]]] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.last_observation: Optional[Observation] = None

    def on_observation(self, handler: Callable[[Observation], Awaitable[Optional[ActionIntent]]]):
        self._observation_handler = handler
        return handler

    def on_event(self, handler: Callable[[EventNotification], Awaitable[None]]):
        self._event_handler = handler
        return handler

    def on_result(self, handler: Callable[[ActionResult], Awaitable[None]]):
        self._result_handler = handler
        return handler

    async def connect(self):
        uri = f"{self.host}/ws/gateway?token={self.jwt_token}"
        self._running = True
        reconnect_delay = 1

        while self._running:
            try:
                async with websockets.connect(uri) as ws:
                    self._ws = ws
                    reconnect_delay = 1
                    logger.info("Connected to Genesis Engine")

                    # Register
                    await self._send(ws, {
                        "type": "agent.register",
                        "msg_id": secrets.token_hex(8),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "payload": {
                            "api_key": self.api_key,
                            "manifest": self.manifest,
                        },
                    })

                    self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(ws))

                    async for raw in ws:
                        try:
                            msg = json.loads(raw)
                            await self._dispatch(msg)
                        except json.JSONDecodeError:
                            logger.warning("Received invalid JSON")
                        except Exception as e:
                            logger.exception(f"Message handling error: {e}")

            except (websockets.ConnectionClosed, OSError) as e:
                logger.warning(f"Disconnected: {e}. Reconnecting in {reconnect_delay}s...")
                self._ws = None
                if self._heartbeat_task:
                    self._heartbeat_task.cancel()
                if self._running:
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, 30)

    async def disconnect(self):
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()

    async def submit_action(self, intent: ActionIntent):
        if not self._ws:
            logger.warning("Not connected, cannot submit action")
            return
        await self._send(self._ws, {
            "type": "agent.intent",
            "msg_id": secrets.token_hex(8),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": intent.model_dump(),
        })

    async def push_memory(self, summary: MemorySummary):
        if not self._ws:
            return
        await self._send(self._ws, {
            "type": "memory.summary",
            "msg_id": secrets.token_hex(8),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": summary.model_dump(),
        })

    async def _dispatch(self, msg: dict):
        msg_type = msg.get("type", "")
        payload = msg.get("payload", {})

        if msg_type == "world.observation":
            obs = Observation(**payload)
            self.last_observation = obs
            if self._observation_handler:
                intent = await self._observation_handler(obs)
                if intent:
                    await self.submit_action(intent)

        elif msg_type == "action.result":
            result = ActionResult(**payload)
            if self._result_handler:
                await self._result_handler(result)

        elif msg_type == "event.notification":
            event = EventNotification(**payload)
            if self._event_handler:
                await self._event_handler(event)

        elif msg_type == "system.warning":
            warning = Warning(**payload)
            logger.warning(f"[{warning.code}] {warning.message}")

        elif msg_type == "system.welcome":
            logger.info(f"Welcome! World: {payload.get('world_id')}, Tick: {payload.get('current_tick')}")

    async def _heartbeat_loop(self, ws):
        while True:
            try:
                await asyncio.sleep(30)
                await self._send(ws, {
                    "type": "agent.heartbeat",
                    "msg_id": secrets.token_hex(8),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": {"status": "active"},
                })
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                break

    @staticmethod
    async def _send(ws, data: dict):
        await ws.send(json.dumps(data, default=str))

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and not self._ws.closed

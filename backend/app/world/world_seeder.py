"""Seeds the initial Aethermoor world: locations, connections, organizations, and NPC agents."""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.world import World
from app.models.location import Location, LocationConnection
from app.models.organization import Organization, OrganizationMember
from app.models.agent import Agent
from app.core.constants import AgentType, AgentStatus

logger = logging.getLogger(__name__)

LOCATIONS = [
    {"name": "Town Square", "type": "plaza", "x": 0.5, "y": 0.5, "capacity": 50},
    {"name": "Market", "type": "market", "x": 0.65, "y": 0.4, "capacity": 30},
    {"name": "Tavern", "type": "tavern", "x": 0.35, "y": 0.35, "capacity": 25},
    {"name": "Guild Hall", "type": "guild", "x": 0.7, "y": 0.6, "capacity": 20},
    {"name": "Park", "type": "park", "x": 0.5, "y": 0.25, "capacity": 40},
    {"name": "Library", "type": "library", "x": 0.3, "y": 0.6, "capacity": 15},
    {"name": "Blacksmith", "type": "workshop", "x": 0.75, "y": 0.75, "capacity": 10},
    {"name": "Council Hall", "type": "council", "x": 0.5, "y": 0.7, "capacity": 30},
    {"name": "Harbor", "type": "harbor", "x": 0.2, "y": 0.5, "capacity": 35},
]

# (from_name, to_name) — bidirectional
CONNECTIONS = [
    ("Town Square", "Market"),
    ("Town Square", "Tavern"),
    ("Town Square", "Park"),
    ("Town Square", "Council Hall"),
    ("Market", "Guild Hall"),
    ("Market", "Blacksmith"),
    ("Tavern", "Harbor"),
    ("Tavern", "Park"),
    ("Council Hall", "Library"),
    ("Council Hall", "Guild Hall"),
    ("Harbor", "Market"),
    ("Library", "Park"),
]

ORGANIZATIONS = [
    {"name": "Merchants Guild", "type": "guild"},
    {"name": "Town Council", "type": "council"},
    {"name": "Adventurers Society", "type": "faction"},
]

NPC_ROLES = [
    ("merchant", "Merchants Guild", 8),
    ("town_crier", None, 2),
    ("guard", None, 5),
    ("elder", "Town Council", 3),
    ("citizen", None, 32),  # generic citizens
]


async def seed_world(world_id: uuid.UUID, db: AsyncSession, owner_user_id: uuid.UUID):
    result = await db.execute(select(Location).where(Location.world_id == world_id).limit(1))
    if result.scalar_one_or_none():
        logger.info("World already seeded, skipping.")
        return

    logger.info("Seeding Aethermoor world...")

    # Create locations
    loc_map: dict[str, Location] = {}
    for loc_data in LOCATIONS:
        loc = Location(
            world_id=world_id,
            name=loc_data["name"],
            location_type=loc_data["type"],
            x_coord=loc_data["x"],
            y_coord=loc_data["y"],
            capacity=loc_data["capacity"],
        )
        db.add(loc)
        loc_map[loc_data["name"]] = loc
    await db.flush()

    # Refresh to get IDs
    for loc in loc_map.values():
        await db.refresh(loc)

    # Create bidirectional connections
    for from_name, to_name in CONNECTIONS:
        from_loc = loc_map[from_name]
        to_loc = loc_map[to_name]
        db.add(LocationConnection(from_location_id=from_loc.id, to_location_id=to_loc.id))
        db.add(LocationConnection(from_location_id=to_loc.id, to_location_id=from_loc.id))
    await db.flush()

    # Create organizations
    org_map: dict[str, Organization] = {}
    for org_data in ORGANIZATIONS:
        org = Organization(
            world_id=world_id,
            name=org_data["name"],
            org_type=org_data["type"],
        )
        db.add(org)
        org_map[org_data["name"]] = org
    await db.flush()
    for org in org_map.values():
        await db.refresh(org)

    # Create NPC agents
    spawn_location = loc_map["Town Square"]
    location_list = list(loc_map.values())

    import random
    npc_count = 0
    for role, org_name, count in NPC_ROLES:
        for i in range(count):
            npc_loc = random.choice(location_list)
            npc = Agent(
                owner_user_id=owner_user_id,
                world_id=world_id,
                location_id=npc_loc.id,
                agent_type=AgentType.NPC,
                display_name=f"{role.title()}-{npc_count + 1}",
                status=AgentStatus.ONLINE,
                role=role,
                reputation=random.randint(0, 20),
                influence=random.randint(0, 5),
                permission_level=2,
            )
            db.add(npc)
            npc_count += 1
        await db.flush()

        if org_name and org_name in org_map:
            result = await db.execute(
                select(Agent).where(
                    Agent.world_id == world_id,
                    Agent.role == role,
                    Agent.agent_type == AgentType.NPC,
                ).limit(count)
            )
            npcs = list(result.scalars().all())
            for npc in npcs:
                member = OrganizationMember(
                    org_id=org_map[org_name].id,
                    agent_id=npc.id,
                    role="member",
                )
                db.add(member)
            await db.flush()

    logger.info(f"Seeded {npc_count} NPC agents in {len(loc_map)} locations.")

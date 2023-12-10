from pydantic import BaseModel

from cases.database import database_connection as db


class Edition(BaseModel):
    id: int
    name: str


class List(BaseModel):
    id: int
    first_name: str
    last_name: str
    affiliation: str
    place: int
    edition: int


async def get_editions():
    res = await db.fetch_all("SELECT * FROM editions ORDER BY id DESC")

    return res


async def get_edition(id: int):
    res = await db.fetch_one("SELECT * FROM editions WHERE id = :id", {"id": id})

    return res


async def get_list(id: int):
    res = await db.fetch_all("SELECT * FROM lists WHERE edition = :id", {"id": id})

    return res

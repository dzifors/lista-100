from enum import IntEnum

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


class SortingOptions(IntEnum):
    Ascending = 0
    Descending = 1


async def get_editions(sort: SortingOptions | None = None):
    query = "SELECT * FROM editions"

    if sort == SortingOptions.Descending:
        query += " ORDER BY id DESC"

    res = await db.fetch_all(query)

    return res


async def get_edition_count():
    res = await db.fetch_val("SELECT COUNT(*) count FROM editions")

    return res


async def get_edition(edition: int):
    res = await db.fetch_one("SELECT * FROM editions WHERE id = :id", {"id": edition})

    return res


async def create_edition(name: str):
    res = await db.execute("INSERT INTO editions (name) VALUES (:name)", {"name": name})

    return res


async def delete_edition(edition: int):
    res = await db.execute("DELETE FROM editions WHERE id = :id", {"id": edition})

    return res


async def get_list(edition: int):
    res = await db.fetch_all("SELECT * FROM lists WHERE edition = :id", {"id": edition})

    return res


async def fill_list(edition: int, entry_list: list[list[str]]):
    query = (
        "INSERT INTO lists (first_name, last_name, affiliation, place, edition) VALUES "
    )
    query_inserts = []

    for item in entry_list:
        query_inserts.append(
            f"('{item[1]}', '{item[2]}', '{item[3]}', {int(item[0][:1])}, {edition})"
        )

    query += ",".join(query_inserts)

    return query


async def get_capitule_count():
    res = await db.fetch_val("SELECT COUNT(*) count FROM capitule")

    return res


async def get_capitule():
    res = await db.fetch_all("SELECT * FROM capitule")

    return res

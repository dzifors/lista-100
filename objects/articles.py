from pydantic import BaseModel
from datetime import datetime

from cases.database import database_connection as db


class Article(BaseModel):
    id: int
    title: str
    content: str
    publish_date: datetime


async def get_article(id: int):
    res = await db.fetch_one("SELECT * FROM articles WHERE id = :id", {"id": id})
    print(res)

    return res


async def get_articles(limit: int = 10):
    res = await db.fetch_all(
        "SELECT * FROM articles ORDER BY publish_date DESC LIMIT :limit",
        {"limit": limit},
    )

    return res


async def create_article(title: str, content: str):
    await db.execute(
        "INSERT INTO articles (title, content, publish_date) VALUES (:title, :content, NOW())",
        {"title": title, "content": content},
    )


async def update_article(id: int, title: str, content: str):
    await db.execute(
        "UPDATE articles SET content = :content, title = :title WHERE id = :id",
        {"title": title, "content": content, "id": id},
    )

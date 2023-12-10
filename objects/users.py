from datetime import datetime
from pydantic import BaseModel
from cases.database import database_connection as db
from cases.utils import flash_login


class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    registered_since: datetime
    last_login: datetime


class UserAuth(User):
    auth_hash: str


async def get_user(email: str):
    res = await db.fetch_one(
        "SELECT * FROM users WHERE email = :email", {"email": email}
    )

    return UserAuth(**res) if res else None


async def update_last_login(email: str):
    await db.execute(
        "UPDATE users SET last_login = :last_login WHERE email = :email",
        {"last_login": datetime.now(), "email": email},
    )


def logout(request):
    response = flash_login(request, "Wylogowano pomyślnie.", "success")
    response.delete_cookie(key="token")
    response.delete_cookie(key="token_type")

    return response

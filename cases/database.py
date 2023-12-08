import databases
from objects import settings

database_connection = databases.Database(settings.SQL_URI)


async def init_pool():
    await database_connection.connect()


async def close_pool():
    await database_connection.disconnect()

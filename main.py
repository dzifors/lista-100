#!/usr/bin/env python3
""" Lista 100 """
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn

import routes
from cases import database as db
from cases.logging import Colors, log
from cases.utils import render_template


@asynccontextmanager
async def lifespan(_):
    try:
        await db.init_pool()
        log("Database initialized", Colors.GREEN)
    except Exception as e:
        log(f"Database initialization failed: {e}", Colors.RED)
        os._exit(0)

    log("Startup completed successfully", Colors.MAGENTA)

    yield

    if db.database_connection.is_connected:
        await db.close_pool()
        log(f"Database closed", Colors.GREEN)

    log("Server shut down successfully", Colors.MAGENTA)


app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes.router)


@app.exception_handler(404)
async def page_not_found(request: Request, _):
    return render_template("404.html", request)


def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        server_header=False,
        date_header=False,
        reload=True,
    )


if __name__ == "__main__":
    main()

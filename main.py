from pathlib import Path

import fastapi
import uvicorn
import re
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status, Request
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles
from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config
from fastapi.middleware.cors import CORSMiddleware
from typing import Callable
from fastapi.responses import JSONResponse

app = fastapi.FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


user_agent_ban_list = [r"Python-urllib"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    The user_agent_ban_middleware function is a middleware function that checks the user-agent header of an incoming request.
    If the user-agent matches any of the patterns in our ban list, then we return a 403 Forbidden response with an error message.
    Otherwise, we call next and let FastAPI handle it.

    :param request: Request: Get the user-agent from the request headers
    :param call_next: Callable: Pass the next middleware function in the chain to be called
    :return: A jsonresponse object if the user_agent matches one of the banned patterns

    """
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A value that is passed to the fastapi instance

    """
    r = await redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    await FastAPILimiter.init(r)


@app.get("/")
def index():
    """
    The index function is the default function that will be called when a user
    visits the root of your API. It returns a simple message to let users know
    that they have successfully connected to your API.

    :return: A dictionary in json format

    """
    return {"message": "Hello world"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is up and running.
    It does this by making a request to the database, which will raise an exception if it's not working.

    :param db: AsyncSession: Inject the database session
    :return: A json object with a message

    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

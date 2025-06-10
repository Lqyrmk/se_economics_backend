from contextlib import asynccontextmanager

import uvicorn

from routers import items, hero, estimation
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(items.router)
app.include_router(hero.router)
app.include_router(estimation.router)

origins = [
    "http://localhost",
    "http://localhost:9000",  # front-end
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)

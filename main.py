from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import estimation, budget_cost, risk, scheduler
from app.dependencies import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(estimation.router)
app.include_router(budget_cost.router)
app.include_router(risk.router)
app.include_router(scheduler.router)

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

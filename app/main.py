import uvicorn

from typing import Union
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import items

app = FastAPI()

app.include_router(items.router)

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

import uvicorn

from typing import Union
from fastapi import Depends, FastAPI
from routers import items

app = FastAPI()

app.include_router(items.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)

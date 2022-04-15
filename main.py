import uvicorn
from fastapi import FastAPI


from src.api import map, urls, mockorder, capitainauth, customerauth
from src.db.database import create_db

create_db()
app = FastAPI()
app.include_router(map.router)
app.include_router(urls.router)
app.include_router(mockorder.router)
app.include_router(capitainauth.router)
app.include_router(customerauth.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

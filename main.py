import uvicorn
from fastapi import FastAPI


from src.api import map, mockorder, customerauth, captainauth, clienturls, captanurls
from src.db.database import create_db

create_db()
app = FastAPI()
app.include_router(map.router)
app.include_router(clienturls.router)
app.include_router(mockorder.router)
app.include_router(captainauth.router)
app.include_router(captanurls.router)
app.include_router(customerauth.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

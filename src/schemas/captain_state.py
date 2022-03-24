from pydantic import BaseModel


class Coordinates(BaseModel):
    longitude: float
    latitude: float
    timestamp: int
    accuracy: float
    altitude: float
    floor: str
    heading: float
    speed: float
    speed_accuracy: float
    is_mocked: bool


class Body(BaseModel):
    state: int
    coordinates: Coordinates


class CaptainState(BaseModel):
    header: str
    body: Body

from typing import List

from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class Pier(BaseModel):
    id: int
    name: str
    coordinates: Coordinates


class Boat(BaseModel):
    id: int
    name: str
    boat_rating: float
    captian_rating: float
    images: List[str]
    cost: int
    piers: List[Pier]

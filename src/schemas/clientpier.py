from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class BasePier(BaseModel):
    id: int
    name: str
    rating: float
    coordinates: Coordinates
    images: List[str]


class PierWIthImages(BasePier):
    images: List[str]


class ClientPier(BaseModel):
    version: int
    piers: List[PierWIthImages]

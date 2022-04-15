from textwrap import indent
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.db.database import Base


class Captain(Base):
    __tablename__ = "captains"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String)
    raiting = Column(Float)
    boat_id = relationship("Boat", backref="captains", uselist=False)


class Boat(Base):
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    boat_raiting = Column(Float)
    cost = Column(Float)
    description = Column(String)
    length = Column(Float)
    power = Column(Integer)
    capacity = Column(Integer)
    captain_id = Column(Integer, ForeignKey("captains.id"))
    pier_id = relationship("Pier", backref="boats")
    image_id = relationship("Image", backref="boats")
    order_id = relationship("Order", backref="boats")
    coord_id = relationship("BoatCoordinate", backref="boats")


class Pier(Base):
    __tablename__ = "piers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    rating = Column(Float)
    description = Column(String)
    boat_id = Column(Integer, ForeignKey("boats.id"))
    order_id = relationship("Order", backref="piers")
    image_id = relationship("PierImage", backref="piers")


class PierImage(Base):
    __tablename__ = "pier_images"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
    pier_id = Column(Integer, ForeignKey("piers.id"))


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
    boat_id = Column(Integer, ForeignKey("boats.id"))


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    order_id = relationship("Order", backref="clients")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    time_created = Column(DateTime())
    order_state = Column(Integer)
    minTimeOrder = Column(Integer)
    client_id = Column(Integer, ForeignKey("clients.id"))
    boat_id = Column(Integer, ForeignKey("boats.id"))
    pier_id = Column(Integer, ForeignKey("piers.id"))


class BoatCoordinate(Base):
    __tablename__ = "boat_coordinates"

    id = Column(Integer, primary_key=True, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    state = Column(Integer)
    boat_id = Column(Integer, ForeignKey("boats.id"))

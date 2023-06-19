from dataclasses import dataclass
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

@dataclass
class Location(Base):
    __tablename__ = "locations"
    id = Column(String, primary_key = True)
    name: str = ""
    url: str = ""
    food_url: str = ""
    fun_url: str = ""
    hotel_url: str = ""
    place_type: str = ""
    pos: tuple[float, float] = (-1, -1)
    

@dataclass
class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(String, primary_key = True)
    name: str = ""
    url: str = ""
    rating: int = -1
    review_count: int = -1
    price: str = ""
    tags: list[str] = field(default_factory = list)
    imgs: list[str] = field(default_factory = list)
    contact: dict = field(default_factory = dict)
    
engine = create_engine("sqlite://mydb.sqlite")
Base.metadata.create_all(engine)
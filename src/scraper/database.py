from pathlib import Path
from dataclasses import dataclass, field

from sqlalchemy import String, create_engine, Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker
)


class Base(DeclarativeBase):
    pass


@dataclass
class Location():
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
    id: Mapped[str] = mapped_column(String, primary_key = True, default = "")
    name: Mapped[str] = mapped_column(String, default = "")
    url: Mapped[str] = mapped_column(default = "")
    rating: Mapped[float] = mapped_column(default = -1.0)
    review_count: Mapped[int] = mapped_column(default = -1)
    price: Mapped[str] = mapped_column(default = "")
    tags: Mapped[str] = mapped_column(String, default = "")
    imgs: Mapped[str] = mapped_column(String, default = "")
    address: Mapped[str] = mapped_column(default = "")
    phone: Mapped[str] = mapped_column(default = "")
    

dir = Path(__file__).resolve().parent
engine = create_engine(f"sqlite:///{dir}/scrape.db")
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
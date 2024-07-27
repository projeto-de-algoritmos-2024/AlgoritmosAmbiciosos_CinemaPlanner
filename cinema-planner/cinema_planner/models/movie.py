from sqlalchemy import Column, Integer, String
from cinema_planner.db import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    overview = Column(String)
    runtime = Column(String)
    release_date = Column(String)

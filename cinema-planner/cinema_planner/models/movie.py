from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from cinema_planner.db import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    overview = Column(String)
    runtime = Column(Integer)
    release_date = Column(String)
    show_times = relationship("ShowTime", back_populates="movie")

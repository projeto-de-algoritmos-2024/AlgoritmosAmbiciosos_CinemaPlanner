from cinema_planner.db import Base
from sqlalchemy import Column, Integer, Time, ForeignKey
from sqlalchemy.orm import relationship


class ShowTime(Base):
    __tablename__ = "showtimes"
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    time = Column(Time)
    movie = relationship("Movie", back_populates="show_times")

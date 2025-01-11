from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from .fridges import Fridges, FridgesSupplementary
from .sensors import Sensors, SensorsSupplementary

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(Base)

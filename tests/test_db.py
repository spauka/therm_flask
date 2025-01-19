import labmon
from labmon.db import Base
from labmon.db.fridges import Fridge, FridgeSupplementary
from labmon.db.sensors import Sensor, SensorSupplementary

from sqlalchemy.schema import CreateTable

app = labmon.create_app()
db = labmon.db.db

with app.app_context():
    engine = db.engine
    fridge = Fridge.get_fridge_by_name("Blue Fridge")
    print(fridge.name)
    fridge_table = fridge.fridge_table()
    print(fridge_table)

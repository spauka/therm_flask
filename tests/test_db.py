import labmon
from labmon.db import Base
from labmon.db.fridges import Fridge, FridgeSupplementary
from labmon.db.sensors import Sensor, SensorSupplementary

from sqlalchemy.schema import CreateTable

app = labmon.create_app()
db = labmon.db.db

with app.app_context():
    engine = db.engine
    # Base.metadata.create_all(engine)
    fridge_query = db.select(Fridge).where(Fridge.fridge_id == 1)
    fridge = db.session.execute(fridge_query).fetchone()
    print(fridge)
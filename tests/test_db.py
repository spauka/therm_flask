from pprint import pprint
from datetime import datetime

import labmon
from labmon.db import (
    Fridge,
    FridgeSupplementary,
    Sensor,
    SensorSupplementary,
)

app = labmon.create_app()
db = labmon.db.db

with app.app_context():
    engine = db.engine
    fridge = Fridge.get_fridge_by_name("Blue_Fridge")
    print(fridge.name)
    fridge_table = fridge.fridge_table()
    print(f"Fridge table: {fridge_table} with {fridge_table.size()} records")
    last_3 = list(fridge_table.get_last(3))
    pprint(last_3)
    last_year = list(
        fridge_table.get_between(
            datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 9, 5, 0)
        )
    )
    pprint(last_year)
    hourly = list(fridge_table.hourly_avg(count=10))
    pprint(hourly)

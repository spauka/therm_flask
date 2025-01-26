import re

from sqlalchemy import text
from sqlalchemy.schema import CreateTable

import labmon
from labmon.db import (
    Fridge,
)
from labmon.db.db import Base

app = labmon.create_app()
db = labmon.db.db

def transition_table(fridge, fridge_table, old_name, new_name):
    print(f"Transitioning {old_name} -> {new_name}")

    # First, drop the new table if it exists
    db.session.execute(text(f"DROP TABLE IF EXISTS \"{new_name}\""))

    # Then create the new table
    create = str(CreateTable(fridge_table.__table__).compile(dialect=db.engine.dialect))
    create = re.sub(r",\s+PRIMARY KEY \(time\)", "", create, flags=re.MULTILINE)
    print(create)
    db.session.execute(text(create))

    # Convert to a timescale hypertable
    hyper = text(f"SELECT create_hypertable('{new_name}', by_range('time', INTERVAL '1 month'))")
    print(hyper)
    db.session.execute(hyper)

    # Copy across data from old table
    columns = [f"\"{sensor.column_name}\"" for sensor in fridge.sensors if sensor.column_name != "time"]
    insert = text(f"INSERT INTO \"{new_name}\" (time, {', '.join(columns)}) SELECT * FROM \"{old_name}\" ORDER BY \"Time\" ASC")
    print(insert)
    db.session.execute(insert)

    print(f"Done {new_name}")

with app.app_context():
    # Create mapping from old fridge tables to new fridge tables
    query = text("SELECT f.name AS oldname, f.fridge_table_name AS newname FROM fridges AS f")
    results = list(db.session.execute(query).all())

    for old_name, new_name in results:
        # Construct a new table with the right name. Luckily we can take
        # advantage of the ORM we've defined
        fridge = Fridge.get_fridge_by_name(old_name)
        fridge_table = fridge.fridge_table(check_exists=False)

        # Transition the table
        transition_table(fridge, fridge_table, old_name, new_name)

        # Do this for all supplementary sensors
        for supp in fridge.supplementary:
            old_name = supp.table_name
            new_name = old_name.lower()

            supp.table_name = new_name
            supp_table = supp.fridge_table(check_exists=False)

            transition_table(supp, supp_table, old_name, new_name)


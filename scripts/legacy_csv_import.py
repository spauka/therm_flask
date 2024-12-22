from temp_log import Fridges, db
from app import app

import sys
import os, os.path
import csv
from datetime import datetime

# Starting from a CSV in the old format, import data into the database
def import_data(fridge, data):
    if not isinstance(fridge, Fridges):
        raise TypeError('Fridge must be an instance of Fridges')
    
    data = csv.reader(data, delimiter=',', quotechar='"')
    for line in data:
        values = {}
        values["Time"] = datetime.strptime(line[0], '%a, %d %b %Y %H:%M:%S')
        values["four_K_RuO"] = float(line[2])
        values["Still_RuO"] = float(line[4])
        values["50mK_RuO"] = float(line[6])
        values["MC_CMN"] = float(line[8])
        values["MC_PT"] = float(line[10])

        # Insert data into database
        fridge.append(**values)

if __name__ == "__main__":
    db.app = app
    db.init_app(app)

    if len(sys.argv) != 3:
        print("Usage: %s <fridge> <data_file>")
        exit(1)

    fridge = sys.argv[1].replace('_', ' ')
    fridge = Fridges.query.filter_by(name=fridge)
    if fridge.count() == 0:
        print("Unable to find fridge %s." % fridge)
        exit(1)

    fridge = fridge.first()

    data = sys.argv[2]
    if not os.path.exists(data):
        print("Unable to find data file %s." % data)
        exit(1)

    data = open(data, 'rU')
    columns = csv.reader(data, delimiter=',', quotechar='"')
    print(columns.next())
    prompt = raw_input("Does the header look OK? (Y, N) ")
    if prompt == "N":
        exit(0)
    if prompt != "Y":
        exit(1)
    data.seek(0)

    import_data(fridge, data)

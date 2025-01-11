from temp_log import Fridges, db
from app import app

db.app = app
db.init_app(app)

b = Fridges.query.filter_by(name='Blue Fridge').first()
r = Fridges.query.filter_by(name='Red Fridge').first()
big = Fridges.query.filter_by(name='Big Fridge').first()
bf = Fridges.query.filter_by(name='BlueFors LD').first()

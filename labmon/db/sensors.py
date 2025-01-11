from . import db, Fridges, FridgesSupplementary


class Sensors(db.Model, db.Column):
    """
    List of sensors attached to the fridge given by fridge_id
    """
    id = db.Column(db.Integer(), primary_key=True)
    fridge_id = db.Column(db.Integer(), db.ForeignKey('Fridges.id'))
    column_name = db.Column(db.String(1024))
    display_name = db.Column("name", db.String(1024))
    view_order = db.Column(db.Integer())
    visible = db.Column(db.Integer())
    __tablename__ = "sensors"

    def __init__(self, display_name, column_name, fridge, view_order=1, visible=1):
        if isinstance(fridge, Fridges):
            self.fridge_id = fridge.id
        else:
            self.fridge_id = int(fridge)
        self.display_name = display_name
        self.column_name = column_name
        self.view_order = view_order
        self.visible = visible

        db.Column.__init__(self, column_name, db.Float)

    def __repr__(self):
        return f"<Sensor {self.column_name}>"

    @classmethod
    def get_sensor(cls, name, fridge, add=False):
        if isinstance(fridge, Fridges):
            fridge_id = fridge.id
        else:
            fridge_id = int(fridge)

        sensor = cls.query.filter_by(column_name=name, fridge_id=fridge_id)
        if sensor.count() == 0 and add:
            safe_name = name.replace(' ', '_')
            sensor = Sensors(name, safe_name, fridge)
            db.session.add(sensor)
            return sensor
        elif sensor.count() == 0 and not add:
            raise KeyError("Sensor not found")
        return sensor.first()

class SensorsSupplementary(db.Model):
    """
    List of sensors attached to the supplementary sensor set
    """
    id = db.Column(db.Integer(), primary_key=True)
    fridge_suppl_id = db.Column(db.Integer(), db.ForeignKey('FridgesSupplementary.id'))
    column_name = db.Column(db.String(1024))
    display_name = db.Column("name", db.String(1024))
    view_order = db.Column(db.Integer())
    visible = db.Column(db.Integer())
    __tablename__ = "sensors_supplementary"

    def __init__(self, name, fridge_suppl, column_name=None, view_order=1, visible=1):
        if isinstance(fridge_suppl, FridgesSupplementary):
            self.fridge_suppl_id = fridge_suppl.id
        else:
            self.fridge_suppl_id = int(fridge_suppl)
        self.column_name = name
        if column_name:
            self.column_name = column_name
        else:
            self.column_name = name
        self.view_order = view_order
        self.visible = visible

    def __repr__(self):
        return f"<Supplementary_Sensor {self.column_name}>"

    @classmethod
    def get_sensor(cls, name, fridge, add=False):
        if isinstance(fridge, FridgesSupplementary):
            suppl_id = fridge.id
        else:
            suppl_id = int(fridge)

        sensor = cls.query.filter_by(column_name=name, fridge_suppl_id=suppl_id)
        if sensor.count() == 0 and add:
            sensor = SensorsSupplementary(name, fridge, name)
            db.session.add(sensor)
            return sensor
        elif sensor.count() == 0 and not add:
            raise KeyError("Unknown Sensor")
        return sensor.first()

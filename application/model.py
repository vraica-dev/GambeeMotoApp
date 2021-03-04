from . import db


class TripRecords(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100))
    area_name = db.Column(db.String(50))
    km_travelled = db.Column(db.Integer)
    h_travelled = db.Column(db.Integer)

    def __init__(self, trip_name, area_name, km_travelled, h_travelled):
        self.trip_name = trip_name
        self.area_name = area_name
        self.km_travelled = km_travelled
        self.h_travelled = h_travelled


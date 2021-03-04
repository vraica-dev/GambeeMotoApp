from application import db


class TripRecords(db.Model):
    __tablename__ = 'TripRecords'
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100))
    area_name = db.Column(db.String(50))
    km_travelled = db.Column(db.Integer)
    h_travelled = db.Column(db.Integer)
    km_initial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)

    def __init__(self, trip_name, area_name, km_travelled, h_travelled, km_initial, km_final):
        self.trip_name = trip_name
        self.area_name = area_name
        self.km_travelled = km_travelled
        self.h_travelled = h_travelled
        self.km_initial = km_initial
        self.km_final = km_final

    def __repr__(self):
        return f'Trip name: {self.trip_name}\nTrip area: {self.area_name}\nKM done: {self.km_travelled}\nHours of Riding: {self.h_travelled}\n'



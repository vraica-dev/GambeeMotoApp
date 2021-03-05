from application import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class TripRecords(db.Model):
    __tablename__ = 'TripRecords'
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100))
    area_name = db.Column(db.String(50))
    km_travelled = db.Column(db.Integer)
    h_travelled = db.Column(db.Integer)
    km_initial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)
    added_by = db.Column(db.String(100))

    def __init__(self, trip_name, area_name, km_travelled, h_travelled, km_initial, km_final, added_by):
        self.trip_name = trip_name
        self.area_name = area_name
        self.km_travelled = km_travelled
        self.h_travelled = h_travelled
        self.km_initial = km_initial
        self.km_final = km_final
        self.added_by = added_by

    def __repr__(self):
        return f'Trip name: {self.trip_name}\nTrip area: {self.area_name}\nKM done: {self.km_travelled}\nHours of Riding: {self.h_travelled}\nAdded by: {self.added_by}'



class Riders(db.Model, UserMixin):
    __tablename__ = 'Users_Tab'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    passw = db.Column(db.String(50))

    def __init__(self, email, passw):
        self.email = email
        self.passw = passw

    def check_password(self, password):
        return self.passw == password

    def get_id(self):
        return self.email



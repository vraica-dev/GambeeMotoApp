from application import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class TripRecords(db.Model):
    __tablename__ = 'TripRecords'
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100))
    trip_date = db.Column(db.Date)
    area_name = db.Column(db.String(50))
    km_travelled = db.Column(db.Integer)
    h_travelled = db.Column(db.Integer)
    km_initial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)
    added_by = db.Column(db.String(100))

    def __init__(self, trip_name, trip_date, area_name, km_travelled, h_travelled, km_initial, km_final, added_by):
        self.trip_name = trip_name
        self.trip_date = trip_date
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
    email = db.Column(db.String(100), unique=True)
    passw = db.Column(db.String(50))
    joined_on = db.Column(db.Date)

    def __init__(self, email, passw):
        self.email = email
        self.passw = None
        self.joined_on = datetime.now().date()

    def set_passw(self, password):
        self.passw = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(self.passw, password)

    def get_id(self):
        return self.email



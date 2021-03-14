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


class MechanicalEvent(db.Model):
    __tablename__ = 'Mechanical_Tab'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100))
    event_date = db.Column(db.Date)
    event_details = db.Column(db.String(200))
    event_km = db.Column(db.Integer)
    event_cost = db.Column(db.Float)
    event_owner = db.Column(db.String(100))

    def __init__(self, event_name, event_date, event_details, event_km, event_cost, event_owner):
        self.event_name = event_name
        self.event_date = event_date
        self.event_details = event_details
        self.event_km = event_km
        self.event_cost = event_cost
        self.event_owner = event_owner


class TripPicture(db.Model):
    __tablename__ = 'Trip_Pictures'
    id = db.Column(db.Integer, primary_key=True)
    pic_name = db.Column(db.String(100))
    pic_location = db.Column(db.String(100))
    pic_blob = db.Column(db.BLOB)
    pic_owner = db.Column(db.String(100))
    pic_posted_on = db.Column(db.Date)

    def __init__(self, pic_name, pic_location, pic_blob, pic_owner):
        self.pic_name = pic_name
        self.pic_location = pic_location
        self.pic_blob = pic_blob
        self.pic_owner = pic_owner
        self.pic_posted_on = datetime.now().date()

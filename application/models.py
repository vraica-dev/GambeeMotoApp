from datetime import date, datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from application import db


class TripRecords(db.Model):  # type: ignore[name-defined]
    __tablename__ = "TripRecords"
    __table_args__ = (
        db.UniqueConstraint("added_by", "trip_name", name="uq_trips_owner_name"),
    )
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100), nullable=False)
    trip_date = db.Column(db.Date)
    area_name = db.Column(db.String(50))
    km_travelled = db.Column(db.Integer)
    h_travelled = db.Column(db.Integer)
    km_initial = db.Column(db.Integer)
    km_final = db.Column(db.Integer)
    added_by = db.Column(
        db.String(100), db.ForeignKey("Users_Tab.email"), nullable=False, index=True
    )

    def __init__(
        self,
        trip_name: str,
        trip_date: date,
        area_name: str,
        km_travelled: int,
        h_travelled: int,
        km_initial: int,
        km_final: int,
        added_by: str,
    ) -> None:
        self.trip_name = trip_name
        self.trip_date = trip_date
        self.area_name = area_name
        self.km_travelled = km_travelled
        self.h_travelled = h_travelled
        self.km_initial = km_initial
        self.km_final = km_final
        self.added_by = added_by

    def __repr__(self) -> str:
        return f"Trip name: {self.trip_name}\nTrip area: {self.area_name}\nKM done: {self.km_travelled}\nHours of Riding: {self.h_travelled}\nAdded by: {self.added_by}"


class Riders(db.Model, UserMixin):  # type: ignore[name-defined]
    __tablename__ = "Users_Tab"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    passw = db.Column(db.String(255))
    joined_on = db.Column(db.Date)

    def __init__(self, email: str) -> None:
        self.email = email
        self.passw = None
        self.joined_on = datetime.now().date()

    def set_passw(self, password: str) -> None:
        self.passw = generate_password_hash(password=password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.passw, password)

    def get_id(self) -> str:
        return str(self.id)


class MechanicalEvent(db.Model):  # type: ignore[name-defined]
    __tablename__ = "Mechanical_Tab"
    __table_args__ = (
        db.UniqueConstraint("event_owner", "event_name", name="uq_events_owner_name"),
    )
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.Date)
    event_details = db.Column(db.String(200))
    event_km = db.Column(db.Integer)
    event_cost = db.Column(db.Float)
    event_owner = db.Column(
        db.String(100), db.ForeignKey("Users_Tab.email"), nullable=False, index=True
    )

    def __init__(
        self,
        event_name: str,
        event_date: date,
        event_details: str,
        event_km: int,
        event_cost: float,
        event_owner: str,
    ) -> None:
        self.event_name = event_name
        self.event_date = event_date
        self.event_details = event_details
        self.event_km = event_km
        self.event_cost = event_cost
        self.event_owner = event_owner


class TripPicture(db.Model):  # type: ignore[name-defined]
    __tablename__ = "Trip_Pictures"
    id = db.Column(db.Integer, primary_key=True)
    pic_name = db.Column(db.String(100))
    pic_location = db.Column(db.String(100))
    pic_blob = db.Column(db.BLOB)
    pic_preview = db.Column(db.LargeBinary, nullable=True)
    pic_owner = db.Column(
        db.String(100), db.ForeignKey("Users_Tab.email"), nullable=False, index=True
    )
    pic_posted_on = db.Column(db.Date)

    def __init__(
        self,
        pic_name: str,
        pic_location: str,
        pic_blob: bytes,
        pic_owner: str,
        pic_preview: Optional[bytes] = None,
    ) -> None:
        self.pic_name = pic_name
        self.pic_location = pic_location
        self.pic_blob = pic_blob
        self.pic_owner = pic_owner
        self.pic_preview = pic_preview
        self.pic_posted_on = datetime.now().date()

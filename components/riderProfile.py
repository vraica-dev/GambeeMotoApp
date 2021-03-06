from sqlalchemy import desc
from datetime import datetime
from config import Config


class RiderProfile(object):
    def __init__(self, email, joined_on):
        self.email = email
        self.joined_on = joined_on

        self.tripsDB = None
        self.meventsDB = None

        self.recordset_user = None
        self.recordset_mechanical = None

    def set_tripDB(self, db_object):
        self.tripsDB = db_object

    def set_meventsDB(self, db_object):
        self.meventsDB = db_object

    def get_name(self):
        return self.email

    def get_user_recordset(self):
        if self.email != Config.ADMIN_USER:
            user_rec = self.tripsDB.query.filter_by(added_by=self.email).all()
        else:
            user_rec = self.tripsDB.query.all()
        self.recordset_user = user_rec

    def get_mechanical_recordset(self):
        if self.email != Config.ADMIN_USER:
            user_rec = self.meventsDB.query.filter_by(event_owner=self.email).all()
        else:
            user_rec = self.meventsDB.query.all()
        self.recordset_mechanical = user_rec

    def get_no_posts(self):
        no_of_posts = 0
        for post in self.recordset_user:
            no_of_posts += 1
        return no_of_posts

    def get_total_km(self):
        no_km = 0
        for post in self.recordset_user:
            no_km += post.km_travelled
        return no_km

    def get_total_h(self):
        no_h = 0
        for post in self.recordset_user:
            no_h += post.h_travelled
        return no_h

    def get_days_since_last(self):
        if self.email != Config.ADMIN_USER:
            latest = self.tripsDB.query.filter_by(added_by=self.email).order_by(desc(self.tripsDB.trip_date)).first()
        else:
            latest = self.tripsDB.query.order_by(desc(self.tripsDB.trip_date)).first()

        if latest is not None:
            days_since = (latest.trip_date - datetime.now().date()).days
        else:
            days_since = -1
        return days_since

    def get_no_mevents(self):
        no_events = 0
        for ev in self.recordset_mechanical:
            no_events += 1
        return no_events

    def get_cost_mevents(self):
        cost_events = 0
        for ev in self.recordset_mechanical:
            cost_events += ev.event_cost
        return cost_events
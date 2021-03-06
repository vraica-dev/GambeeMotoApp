from sqlalchemy import desc
from datetime import datetime, timedelta

class RiderProfile(object):
    def __init__(self, email, joined_on):
        self.email = email
        self.joined_on = joined_on
        self.tripsDB = None

    def set_tripDB(self, db_object):
        self.tripsDB = db_object

    def get_name(self):
        return self.email

    def get_view_posts(self):
        list_posts = self.tripsDB.query.filter_by(added_by=self.email).all()
        return list_posts

    def get_no_posts(self):
        list_posts = self.tripsDB.query.filter_by(added_by=self.email).all()
        no_of_posts = 0
        for post in list_posts:
            no_of_posts += 1
        return no_of_posts

    def get_total_km(self):
        list_posts = self.tripsDB.query.filter_by(added_by=self.email).all()
        no_km = 0
        for post in list_posts:
            no_km += post.km_travelled
        return no_km

    def get_total_h(self):
        list_posts = self.tripsDB.query.filter_by(added_by=self.email).all()
        no_h = 0
        for post in list_posts:
            no_h += post.h_travelled
        return no_h

    def get_days_since_last(self):
        latest = self.tripsDB.query.filter_by(added_by=self.email).order_by(desc(self.tripsDB.trip_date)).first()
        days_since = (latest.trip_date -datetime.now().date()).days
        return days_since


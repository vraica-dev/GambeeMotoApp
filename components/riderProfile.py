from datetime import date, datetime
from typing import Any, List, Optional, Union

from sqlalchemy import desc

from config import Config


class RiderProfile:
    def __init__(self, email: str, joined_on: date) -> None:
        self.email = email
        self.joined_on = joined_on

        self.tripsDB: Optional[Any] = None
        self.meventsDB: Optional[Any] = None

        self.recordset_user: Optional[List[Any]] = None
        self.recordset_mechanical: Optional[List[Any]] = None

    def set_tripDB(self, db_object: Any) -> None:
        self.tripsDB = db_object

    def set_meventsDB(self, db_object: Any) -> None:
        self.meventsDB = db_object

    def get_name(self) -> str:
        return self.email

    def get_user_recordset(self) -> None:
        assert self.tripsDB is not None
        if self.email != Config.ADMIN_USER:
            user_rec = self.tripsDB.query.filter_by(added_by=self.email).all()
        else:
            user_rec = self.tripsDB.query.all()
        self.recordset_user = user_rec

    def get_mechanical_recordset(self) -> None:
        assert self.meventsDB is not None
        if self.email != Config.ADMIN_USER:
            user_rec = self.meventsDB.query.filter_by(event_owner=self.email).all()
        else:
            user_rec = self.meventsDB.query.all()
        self.recordset_mechanical = user_rec

    def get_no_posts(self) -> int:
        assert self.recordset_user is not None
        no_of_posts = 0
        for post in self.recordset_user:
            no_of_posts += 1
        return no_of_posts

    def get_total_km(self) -> int:
        assert self.recordset_user is not None
        no_km = 0
        for post in self.recordset_user:
            no_km += post.km_travelled
        return no_km

    def get_total_h(self) -> int:
        assert self.recordset_user is not None
        no_h = 0
        for post in self.recordset_user:
            no_h += post.h_travelled
        return no_h

    def get_days_since_last(self) -> int:
        assert self.tripsDB is not None
        if self.email != Config.ADMIN_USER:
            latest = (
                self.tripsDB.query.filter_by(added_by=self.email)
                .order_by(desc(self.tripsDB.trip_date))
                .first()
            )
        else:
            latest = self.tripsDB.query.order_by(desc(self.tripsDB.trip_date)).first()

        if latest is not None:
            days_since = (latest.trip_date - datetime.now().date()).days
        else:
            days_since = -1
        return days_since

    def get_no_mevents(self) -> int:
        assert self.recordset_mechanical is not None
        no_events = 0
        for ev in self.recordset_mechanical:
            no_events += 1
        return no_events

    def get_cost_mevents(self) -> Union[int, float]:
        assert self.recordset_mechanical is not None
        cost_events = 0
        for ev in self.recordset_mechanical:
            cost_events += ev.event_cost
        return cost_events

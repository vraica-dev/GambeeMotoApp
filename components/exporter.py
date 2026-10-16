"""CSV export built on the ORM -- no raw sqlite3, no temp files, no CWD dependence.

Caller streams ``to_csv()`` straight into the response (see ``main.download_file``).
"""

from typing import Any, Dict, List

import pandas as pd

TRIP_COLUMNS: List[str] = [
    "id",
    "trip_name",
    "trip_date",
    "area_name",
    "km_travelled",
    "h_travelled",
    "km_initial",
    "km_final",
    "added_by",
]
EVENT_COLUMNS: List[str] = [
    "id",
    "event_name",
    "event_date",
    "event_details",
    "event_km",
    "event_cost",
    "event_owner",
]


class DataExporter:
    def __init__(self, active_user: str, query_type: str) -> None:
        if query_type not in ("trips", "events"):
            raise ValueError(f"Unknown export type: {query_type!r}")
        self.active_user = active_user
        self.query_type = query_type

    def _is_admin(self) -> bool:
        from flask import current_app

        return self.active_user == current_app.config["ADMIN_USER"]

    def _rows(self) -> List[Dict[str, Any]]:
        from application.models import MechanicalEvent, TripRecords

        if self.query_type == "trips":
            q = TripRecords.query
            if not self._is_admin():
                q = q.filter_by(added_by=self.active_user)
            return [{c: getattr(t, c) for c in TRIP_COLUMNS} for t in q.all()]
        q = MechanicalEvent.query
        if not self._is_admin():
            q = q.filter_by(event_owner=self.active_user)
        return [{c: getattr(e, c) for c in EVENT_COLUMNS} for e in q.all()]

    def to_csv(self) -> str:
        columns = TRIP_COLUMNS if self.query_type == "trips" else EVENT_COLUMNS
        return pd.DataFrame(self._rows(), columns=columns).to_csv(index=False)

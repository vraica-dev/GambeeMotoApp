from datetime import datetime
from typing import Union

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.wrappers import Response

from application import db
from application.helpers import (
    guest_blocked,
    is_admin,
    is_guest,
    owner_required,
    paginate_query,
    require_email,
)
from application.models import TripRecords

trips_bp = Blueprint("trips", __name__)


@trips_bp.route("/trips", methods=["GET", "POST"])
@login_required
def trips() -> Union[str, Response]:
    if request.method == "GET":
        return render_template("trips.html", crr_user=require_email().split("@")[0])

    if guest_blocked():
        return redirect(url_for("trips.trips"))

    new_trip = TripRecords(
        trip_name=request.form["trip_name"],
        trip_date=datetime.fromisoformat(request.form["trip_date"]),
        area_name=request.form["area_name"],
        km_travelled=int(request.form["km_travelled"]),
        h_travelled=int(request.form["hours_riding"]),
        km_initial=int(request.form["km_initial"]),
        km_final=int(request.form["km_final"]),
        added_by=require_email(),
    )
    db.session.add(new_trip)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You already have a trip with this name.")
    return redirect(url_for("trips.trips"))


@trips_bp.route("/view_trips", methods=["GET"])
@login_required
def view_trips() -> str:
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "", type=str).strip()
    if is_admin():
        base = TripRecords.query
    else:
        base = TripRecords.query.filter_by(added_by=require_email())
    if search:
        like = f"%{search}%"
        base = base.filter(
            (TripRecords.trip_name.ilike(like)) | (TripRecords.area_name.ilike(like))
        )
    trips, page, pages = paginate_query(base.order_by(TripRecords.id.desc()), page)
    return render_template(
        "view_trips.html",
        list_trips=trips,
        crr_user=require_email().split("@")[0],
        page=page,
        pages=pages,
        q=search,
    )


@trips_bp.route("/trip/<int:trip_id>")
@owner_required(TripRecords, "added_by", "trip_id", missing_as_404=True)
def detailed_trip(trip_id: int) -> str:
    return render_template(
        "detailed_trip.html",
        detailed_trip=g.row,
        crr_user=require_email().split("@")[0],
    )


@trips_bp.route("/delete_trip/<int:trip_id>", methods=["POST"])
@owner_required(TripRecords, "added_by", "trip_id")
def delete_trip(trip_id: int) -> Response:
    if is_guest():
        flash("Sorry. You can't delete data as Guest.")
        return redirect(url_for("trips.view_trips"))
    db.session.delete(g.row)
    db.session.commit()
    if is_admin():
        return redirect(url_for("admin.admin_pannel"))
    return redirect(url_for("trips.view_trips"))


@trips_bp.route("/update_trip/<int:trip_id>", methods=["POST"])
@owner_required(TripRecords, "added_by", "trip_id")
def update_existing_trip(trip_id: int) -> Response:
    if is_guest():
        flash("Sorry. You can't save data as Guest.")
        return redirect(url_for("trips.view_trips"))
    trip_existing = g.row
    trip_existing.trip_name = request.form["new_trip_name"]
    trip_existing.trip_date = datetime.fromisoformat(request.form["new_trip_date"])
    trip_existing.area_name = request.form["new_area_name"]
    trip_existing.km_travelled = int(request.form["new_km_travelled"])
    trip_existing.h_travelled = int(request.form["new_hours_riding"])
    trip_existing.km_initial = int(request.form["new_km_initial"])
    trip_existing.km_final = int(request.form["new_km_final"])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You already have a trip with this name.")
    return redirect(url_for("trips.view_trips"))

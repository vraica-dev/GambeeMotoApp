from flask import Blueprint, abort, redirect, render_template, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from application import db
from application.helpers import admin_required, current_email, is_admin
from application.models import MechanicalEvent, Riders, TripPicture, TripRecords

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/ap")
@admin_required
def admin_pannel() -> str:
    all_users = Riders.query.all()
    all_posts = TripRecords.query.all()
    all_events = MechanicalEvent.query.all()
    return render_template(
        "admin_pannel.html", users=all_users, trip_posts=all_posts, mevents=all_events
    )


@admin_bp.route("/delete/<rider_email>", methods=["POST"])
@login_required
def delete_user(rider_email: str) -> Response:
    if not is_admin() and current_email() != rider_email:
        return redirect(url_for("auth.login_page"))

    found_user = Riders.query.filter_by(email=rider_email).first()
    if found_user is None:
        abort(404)
    db.session.delete(found_user)
    for trip in TripRecords.query.filter_by(added_by=rider_email).all():
        db.session.delete(trip)
    for mech in MechanicalEvent.query.filter_by(event_owner=rider_email).all():
        db.session.delete(mech)
    for pic in TripPicture.query.filter_by(pic_owner=rider_email).all():
        db.session.delete(pic)
    db.session.commit()

    if is_admin():
        return redirect(url_for("admin.admin_pannel"))
    return redirect(url_for("auth.login_page"))

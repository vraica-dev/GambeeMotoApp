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
from application.models import MechanicalEvent

events_bp = Blueprint("events", __name__)


@events_bp.route("/mechanical_event", methods=["GET", "POST"])
@login_required
def mechanical_event() -> Union[str, Response]:
    if request.method == "GET":
        return render_template(
            "mechanical_event.html", crr_user=require_email().split("@")[0]
        )

    if guest_blocked():
        return redirect(url_for("events.mechanical_event"))

    new_event = MechanicalEvent(
        event_name=request.form["mevent_name"],
        event_date=datetime.fromisoformat(request.form["mevent_date"]),
        event_details=request.form["mevent_details"],
        event_km=int(request.form["mevent_km"]),
        event_cost=float(request.form["mevent_cost"]),
        event_owner=require_email(),
    )
    db.session.add(new_event)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You already have an event with this name.")
    return redirect(url_for("events.mechanical_event"))


@events_bp.route("/view_mechanical_ev", methods=["GET"])
@login_required
def view_mechanical_ev() -> str:
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "", type=str).strip()
    if is_admin():
        base = MechanicalEvent.query
    else:
        base = MechanicalEvent.query.filter_by(event_owner=require_email())
    if search:
        like = f"%{search}%"
        base = base.filter(
            (MechanicalEvent.event_name.ilike(like))
            | (MechanicalEvent.event_details.ilike(like))
        )
    mevents, page, pages = paginate_query(
        base.order_by(MechanicalEvent.id.desc()), page
    )
    return render_template(
        "view_mechanical_ev.html",
        mevents=mevents,
        crr_user=require_email().split("@")[0],
        page=page,
        pages=pages,
        q=search,
    )


@events_bp.route("/event/<int:event_id>")
@owner_required(MechanicalEvent, "event_owner", "event_id", missing_as_404=True)
def detailed_event(event_id: int) -> str:
    return render_template(
        "detailed_event.html",
        detailed_event=g.row,
        crr_user=require_email().split("@")[0],
    )


@events_bp.route("/delete_event/<int:event_id>", methods=["POST"])
@owner_required(MechanicalEvent, "event_owner", "event_id")
def delete_event(event_id: int) -> Response:
    if is_guest():
        flash("Sorry. You can't delete data as Guest.")
        return redirect(url_for("events.view_mechanical_ev"))
    db.session.delete(g.row)
    db.session.commit()
    if is_admin():
        return redirect(url_for("admin.admin_pannel"))
    return redirect(url_for("events.view_mechanical_ev"))


@events_bp.route("/update_event/<int:event_id>", methods=["POST"])
@owner_required(MechanicalEvent, "event_owner", "event_id")
def update_existing_event(event_id: int) -> Response:
    if is_guest():
        flash("Sorry. You can't save data as Guest.")
        return redirect(url_for("events.view_mechanical_ev"))
    event_existing = g.row
    event_existing.event_name = request.form["new_mevent_name"]
    event_existing.event_date = datetime.fromisoformat(request.form["new_mevent_date"])
    event_existing.event_details = request.form["new_mevent_details"]
    event_existing.event_km = int(request.form["new_mevent_km"])
    event_existing.event_cost = float(request.form["new_mevent_cost"])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You already have an event with this name.")
    return redirect(url_for("events.view_mechanical_ev"))

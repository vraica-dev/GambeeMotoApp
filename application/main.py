import io
from typing import Union

from flask import Blueprint, abort, render_template, send_file
from flask_login import login_required
from werkzeug.wrappers import Response

from application.helpers import is_admin, require_email
from application.models import MechanicalEvent, Riders, TripRecords
from components.exporter import DataExporter
from components.riderProfile import RiderProfile

main_bp = Blueprint("main", __name__)


@main_bp.route("/home")
@login_required
def home() -> str:
    email = require_email()
    return render_template("home.html", crr_user=email.split("@")[0], crr_email=email)


@main_bp.route("/contact")
def contact() -> str:
    return render_template("contact.html")


@main_bp.route("/user/<rider_email>")
@login_required
def user_panel(rider_email: str) -> str:
    active_user = Riders.query.filter_by(email=rider_email).first()
    if active_user is None:
        abort(404)
    if not is_admin() and require_email() != active_user.email:
        abort(403)

    fulL_user = RiderProfile(active_user.email, active_user.joined_on)
    fulL_user.set_tripDB(TripRecords)
    fulL_user.set_meventsDB(MechanicalEvent)
    fulL_user.get_user_recordset()
    fulL_user.get_mechanical_recordset()

    return render_template("user_panel.html", rider_email=fulL_user)


@main_bp.route("/download/<tab>")
@login_required
def download_file(tab: str) -> Union[str, Response]:
    if tab not in ("trips", "events"):
        abort(404)
    csv_text = DataExporter(require_email(), tab).to_csv()
    if not csv_text.strip():
        return f"<p>No file processed for {tab}.</p>"
    buf = io.BytesIO(csv_text.encode("utf-8"))
    filename = f"data_{tab}.csv"
    try:
        return send_file(
            buf, as_attachment=True, download_name=filename, mimetype="text/csv"
        )
    except TypeError:  # Flask 1.x: download_name does not exist yet
        buf.seek(0)
        return send_file(
            buf,
            as_attachment=True,
            attachment_filename=filename,  # type: ignore[call-arg]
            mimetype="text/csv",
        )

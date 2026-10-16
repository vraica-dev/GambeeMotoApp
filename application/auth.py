from typing import Union

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_user, logout_user
from werkzeug.wrappers import Response

from application import db
from application.models import Riders
from components.rate_limit import login_limiter

auth_bp = Blueprint("auth", __name__)

MIN_PASSW_LEN = 8


@auth_bp.route("/", methods=["GET", "POST"])
def login_page() -> Union[str, Response]:
    if request.method == "POST":
        key = request.remote_addr or "unknown"
        if login_limiter.blocked(key):
            abort(429)
        rider_email = request.form["rider_email"]
        rider_passw = request.form["rider_passw"]
        valid_rider = Riders.query.filter_by(email=rider_email).first()
        if valid_rider is not None and valid_rider.check_password(rider_passw):
            login_limiter.reset(key)
            login_user(valid_rider)
            return redirect(url_for("main.home"))
        login_limiter.record(key)
        flash("Wrong Email or Password. Try Again!")
        return redirect(url_for("auth.login_page"))
    logout_user()
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup_page() -> Union[str, Response]:
    if request.method == "POST":
        new_email = request.form["new_email"]
        new_passw = request.form["new_passw"]
        new_passw_second = request.form["new_passw_second"]

        if new_passw != new_passw_second:
            flash("Passwords do not match. Try Again!")
            return render_template("signup.html")

        if len(new_passw) < MIN_PASSW_LEN:
            flash(f"Password must be at least {MIN_PASSW_LEN} characters.")
            return render_template("signup.html")

        if Riders.query.filter_by(email=new_email).first() is not None:
            flash("Email already registered. Try logging in!")
            return render_template("signup.html")

        new_rider_add = Riders(new_email)
        new_rider_add.set_passw(new_passw)
        db.session.add(new_rider_add)
        db.session.commit()
        return redirect(url_for("auth.login_page"))
    logout_user()
    return render_template("signup.html")


@auth_bp.route("/logout")
def log_out() -> Response:
    logout_user()
    return redirect(url_for("auth.login_page"))

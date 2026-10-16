import os
from io import BytesIO
from typing import Optional, Union

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import login_required
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Response

from application import db
from application.helpers import (
    guest_blocked,
    is_admin,
    paginate_query,
    require_email,
)
from application.models import TripPicture
from components.funcs import convert_to_blob
from components.picture_formatter import PicFormatter

pics_bp = Blueprint("pics", __name__)


@pics_bp.route("/trip_pics", methods=["GET", "POST"])
@login_required
def trip_pics() -> Union[str, Response]:
    if request.method == "GET":
        return render_template("trip_pics.html", crr_user=require_email().split("@")[0])

    if guest_blocked():
        return redirect(url_for("pics.trip_pics"))

    temp_pic_name = request.form["pic_name"].strip()
    temp_pic_loc = request.form["pic_loc"]
    temp_pic_data = request.files.get("file")
    temp_pic_owner = require_email()

    if not temp_pic_name or temp_pic_data is None or not temp_pic_data.filename:
        flash("Please choose a picture and give it a name.")
        return redirect(url_for("pics.trip_pics"))
    filename = temp_pic_data.filename.lower()
    if not filename.endswith((".jpg", ".jpeg")):
        flash("Only .jpg/.jpeg pictures are accepted.")
        return redirect(url_for("pics.trip_pics"))
    temp_pic_data.stream.seek(0, os.SEEK_END)
    if temp_pic_data.stream.tell() > 5 * 1024 * 1024:
        flash("Picture must be smaller than 5 MB.")
        return redirect(url_for("pics.trip_pics"))
    temp_pic_data.stream.seek(0)

    try:
        new_pic_formatter = PicFormatter(temp_pic_data)
        ress = new_pic_formatter.get_image_original()
        ress.verify()
        temp_pic_data.stream.seek(0)
        ress = PicFormatter(temp_pic_data).get_image_original()
    except (OSError, ValueError):
        flash("That file is not a valid picture.")
        return redirect(url_for("pics.trip_pics"))
    retreive_pic = os.path.join("application/temp_files", temp_pic_name + ".jpg")
    ress.save(retreive_pic)

    new_pic = TripPicture(
        pic_name=temp_pic_name,
        pic_location=temp_pic_loc,
        pic_blob=convert_to_blob(retreive_pic),
        pic_owner=temp_pic_owner,
        pic_preview=_make_preview(temp_pic_data),
    )
    os.remove(retreive_pic)
    if new_pic:
        db.session.add(new_pic)
        db.session.commit()
    else:
        flash("Error when uploading data")
    return redirect(url_for("pics.trip_pics"))


@pics_bp.route("/view_trip_pics", methods=["GET"])
@login_required
def view_trip_pics() -> str:
    page = request.args.get("page", 1, type=int)
    if is_admin():
        base = TripPicture.query
    else:
        base = TripPicture.query.filter_by(pic_owner=require_email())
    trip_pics, page, pages = paginate_query(base.order_by(TripPicture.id.desc()), page)

    return render_template(
        "view_trip_pics.html",
        list_pics=trip_pics,
        crr_user=require_email().split("@")[0],
        page=page,
        pages=pages,
    )


def _make_preview(upload: FileStorage) -> Optional[bytes]:
    """640px-high JPEG preview; None when the upload can't be thumbnailed."""
    try:
        upload.stream.seek(0)
        thumb = PicFormatter(upload).get_resized_pic().convert("RGB")
        buf = BytesIO()
        thumb.save(buf, format="JPEG")
        return buf.getvalue()
    except (OSError, ValueError):
        return None
    finally:
        try:
            upload.stream.seek(0)
        except (OSError, ValueError):
            pass


def _legacy_preview(pic: TripPicture) -> Optional[bytes]:
    """Generate + persist a preview for pre-thumbnail rows; None on failure."""
    try:
        thumb = PicFormatter(BytesIO(pic.pic_blob)).get_resized_pic().convert("RGB")
        buf = BytesIO()
        thumb.save(buf, format="JPEG")
        pic.pic_preview = buf.getvalue()
        db.session.commit()
        return pic.pic_preview
    except (OSError, ValueError):
        return None


@pics_bp.route("/pic/<int:pic_id>/<size>")
@login_required
def serve_pic(pic_id: int, size: str) -> Response:
    if size not in ("thumb", "full"):
        abort(404)
    pic = TripPicture.query.filter_by(id=pic_id).first()
    if pic is None:
        abort(404)
    if not is_admin() and pic.pic_owner != require_email():
        abort(404)
    data = pic.pic_blob
    if size == "thumb":
        data = pic.pic_preview or _legacy_preview(pic) or pic.pic_blob
    if data is None:
        abort(404)
    response = send_file(BytesIO(data), mimetype="image/jpeg")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response

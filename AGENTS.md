# AGENTS.md — GambeeMotoApp

Flask 1.1.2 moto trip-log app (Jinja + SQLite + Flask-Login). No tests, no lint, no CI, no migrations.

## Run
- Entrypoint: `app.py` → `application:init_app()` (`application/__init__.py`). No app factory args; config is hardcoded (see below).
- Dev server from repo root only: `python app.py` (port `$PORT` or 5000, `debug=True`).
- Install: `pip install -r requirements.txt`. Pinned old stack (`Flask==1.1.2`, `Werkzeug==1.0.1`, `SQLAlchemy==1.3.23`); `runtime.txt` says `python-3.7.0` but will break on modern Python — prefer Python 3.7–3.9 if dependency build fails.
- Prod command in `Procfile` (`flask db upgrade; gunicorn app:app`) is stale: no Flask-Migrate in requirements, so `flask db upgrade` does nothing useful. Schema is created by `db.create_all()` on startup.

## Config / env (required)
- `.env` at repo root loaded by `config.py` via `load_dotenv`: `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `ADMIN_USER`.
- `application/__init__.py` always loads `config.DevConfig` — editing `ProductionConfig` has no effect unless you change that line.
- `ADMIN_USER` email gets cross-user visibility (`view_trips`, `view_mechanical_ev`, `view_trip_pics`, `/ap`, user delete/redirect logic). Test multi-user behavior against it.

## Structure
- `application/routes.py`: all routes (~400 lines, single file). Auth = Flask-Login + `session['logged_user']` checked manually per route; `load_user` looks up by email, not id.
- `application/models.py`: `TripRecords`, `Riders` (`Users_Tab`), `MechanicalEvent` (`Mechanical_Tab`), `TripPicture` (`Trip_Pictures`, BLOB column).
- `components/`: `riderProfile.py` (per-user stats for `user_panel`), `exporter.py` (CSV export via raw sqlite3 + pandas), `picture_formatter.py` (PIL; upload path saves then deletes temp file), `funcs.py` (blob helpers).
- Templates in `application/templates/`, static in `application/static/`.

## Gotchas
- Run from repo root: paths `application/tripsDB.sqlite3` and `application/temp_files/data_{trips,events}.csv` are relative and hardcoded (`exporter.py`, `download_file` route). CWD elsewhere breaks uploads/exports.
- `application/tripsDB.sqlite3` is committed to git. Don't write test data to it; back it up before manual testing, or point `SQLALCHEMY_DATABASE_URI` at a temp copy.
- `application/temp_files/` holds transient upload/CSV files; leave existing files there alone.
- Updates are delete-then-insert (`update_existing_trip`, `update_existing_event`) — ids change, concurrent edits unsafe. Trip/event lookups are by non-unique `trip_name`/`event_name`.
- Auth quirks, don't "fix" silently: signup ignores password confirmation (`new_passw_second` reads the same field); `/user/<email>` uses `startswith` match; several delete/update routes lack `@login_required` and rely only on session checks; guest blocks compare inconsistent strings (`guest@guest.com` vs `XXguest@guest.com`).
- No test suite: verify by booting the server and exercising the touched route manually.

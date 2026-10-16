# PR: Auth + DB hardening and frontend UX/perf (Phases 0–3, Frontend 1–2)

## Summary
Hardens auth/ownership, adds DB integrity + migrations, splits the
monolith route file into blueprints, and lands frontend quick wins:
confirm dialogs, error pages, pagination, search, read-only detail
views, and a thumbnail image pipeline. No test data written to the
committed DB; all verification on temp copies.

## Backend / security
- Fix `LoginManager.session_protection` wiring; `login_view` +
  `session_protection="strong"`.
- `@login_required` on all mutating/private routes; owner-or-admin
  enforcement (`helpers.owner_required`, `admin_required`) with
  `403`/`404` semantics.
- `/user/<email>`: exact match + self-or-admin only (was `startswith`).
- Deletes are POST-only (GET → `405`) + CSRF via Flask-WTF on every
  POST form.
- Signup reads real confirm field, rejects mismatch/duplicate with
  flash; min password length 8.
- Login rate-limit: 5 fails / 5 min / IP → `429`
  (`components/rate_limit.py`).
- `SECRET_KEY` fail-fast; single auth source
  (`helpers.current_email()`); all `session['logged_user']` use removed.
- `get_id()` → numeric id; `load_user` by id with email fallback.

## Data / models / migrations
- FKs + indexes: `added_by`/`event_owner`/`pic_owner` →
  `Users_Tab.email`, `nullable=False`.
- Unique `(owner, name)` on trips/events; `nullable=False` on
  owner/name/email; duplicate create/rename flashes instead of 500.
- `Riders.passw` 50 → 255 (hash truncation fix); `delete_user`
  cascades trips + events + pics.
- Flask-Migrate wired; `db.create_all()` removed; initial revision
  `3f8a1c2d4e5b`. `Procfile`: `flask db upgrade && gunicorn app:app`.
- `TripPicture.pic_preview` (`7c2d9a1b4f6e`, defensive add-column).
- ID-based trip/event routes (`/trip/<int:id>`,
  `/event/<int:id>`); in-place updates preserve `id` (was
  delete-then-insert).

## Structure / exports
- `application/routes.py` (~400 lines) split: `auth`, `main`,
  `trips`, `events`, `pics`, `admin` blueprints + `helpers.py`.
- `exporter.py`: ORM `to_csv()` string, streams `BytesIO` via
  `send_file` — no temp files, no `os.remove` race.
- Full type annotations; `pyproject.toml` (ruff/black/mypy, py37).

## Frontend Phase 1 — quick wins
- Delete `confirm()` on all POST delete forms; custom
  `403/404/405/429/500.html` with home link (`429` retry hint).
- Typo fixes ("KM Initial"); login prefill replaced by "Try the demo
  account" button.
- Pagination (12/page, newest-first, clamped) via
  `helpers.paginate_query` on trips/events/pics; `loading="lazy"`
  on images.

## Frontend Phase 2 — data flow
- Read-only detail cards + explicit Edit toggle; `human_date`
  filter (`01 Jan 2024`).
- Pic upload re-enabled: jpg/jpeg allowlist, 5 MB cap, PIL validity
  check, guidelines note.
- Guest read-only demo banner; `?q=` owner-scoped search on
  trips/events; responsive admin tables (`.table-responsive`,
  `form-narrow`/`detail-wide` + mobile breakpoint).
- Thumbnail pipeline: preview generated at upload
  (`PicFormatter.get_resized_pic`, Pillow 8/10+ compat), served by
  `/pic/<id>/<thumb|full>` with `Cache-Control: public,
  max-age=86400`, owner-checked; legacy rows backfilled lazily;
  list page uses `<img src>` (no inline base64).

## New files
- `application/{auth,main,trips,events,pics,admin,helpers}.py`,
  `components/rate_limit.py`
- `migrations/` (`3f8a1c2d4e5b`, `7c2d9a1b4f6e`),
  `application/templates/{403,405,429,500}.html`, `pyproject.toml`,
  `PLAN.md`, `AGENTS.md`

## Upgrade notes
- Fresh DB: `flask db upgrade`.
- Existing DB: `flask db stamp 3f8a1c2d4e5b && flask db upgrade`.
- Requires `.env`: `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`,
  `ADMIN_USER`. Run from repo root.

## Verification
- Temp-DB checks: anon → login redirect; owner `200`;
  cross-owner `403`/`404`; POST-without-CSRF `400`; 6th bad login
  `429`; pager clamp; search hit/miss; bad upload blocked; legacy
  thumb backfill; custom error bodies.
- Ruff/black/mypy clean on touched Python files.
- Frontend Phase 3 (gunicorn + Postgres, final Locust sweep) pending
  — gated on load numbers.

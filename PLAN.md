# GambeeMotoApp — Execution Plan (single source of truth)

Flask 1.1.2 moto trip-log app (Jinja + SQLite + Flask-Login). Auth + DB hardening roadmap.

**How to use this file:** check off boxes as work lands. Phases 0–3 done; Frontend phases pending.
**Verify rule:** run from repo root (`python app.py`), back up `application/tripsDB.sqlite3`
or point `SQLALCHEMY_DATABASE_URI` at a temp copy before manual testing. Leave
`application/temp_files/` contents alone.

---

## Phase 0 — Baseline ✅ DONE
- [x] Map architecture (`app.py` → `application/__init__.py:init_app()` → `config.DevConfig` → `db.create_all()` → `application/routes.py`)
- [x] Inventory routes/models/helpers (`models.py`: `TripRecords`, `Riders`, `MechanicalEvent`, `TripPicture`; `components/`: `riderProfile`, `exporter`, `picture_formatter`, `funcs`)
- [x] Record manual test flows (login/signup/trip/event/pic)

## Phase 1 — P0 Auth + DB safety ✅ DONE
Goal: close takeover / data-loss holes. No migration required.

Auth:
- [x] Fix `routes.py` `login_manager.session_protection` → `loginMan.session_protection`
- [x] `@login_required` on `delete_user`, `delete_trip`, `update_existing_trip`, `update_existing_event`, `delete_event`, `download_file`, `trip_pics`, `user_panel`
- [x] Owner-or-admin enforcement (`_is_admin()` / `_require_owner_or_admin()` → `403`/`404`)
- [x] `/user/<email>`: `startswith` → exact `filter_by(email=)` + self-or-admin check (`403`, unknown → `404`)
- [x] `download_file`: allowlist `tab in ('trips','events')` → `404` otherwise
- [x] `trip_pics` POST owner = `session['logged_user']` (no `unknown` fallback)
- [x] `delete_user`: `404` on unknown user

DB interaction:
- [x] ID-based routes: `/trip/<int:trip_id>`, `/event/<int:event_id>`, `/update_trip/<int:trip_id>`, `/update_event/<int:event_id>`, `/delete_trip/<int:trip_id>`, `/delete_event/<int:event_id>` (drops `$`-split hack + non-unique name lookups)
- [x] In-place updates (single `commit`, `id` preserved) replace delete-then-insert
- [x] Templates updated to `*_id` links: `view_trips`, `detailed_trip`, `view_mechanical_ev`, `detailed_event`, `admin_pannel`

Verified (temp DB copy, committed DB untouched):
- [x] Anon → `401` on guarded routes; owner `200`; cross-owner detail `404`; cross-owner delete/update `403`
- [x] Own update preserves `id`; `/user/vraica` prefix → `404`; bad tab authed → `404`; admin sees all + `/ap 200`
- [x] Legacy name URLs now `404` (no redirect shim — accepted)

## Phase 2 — P1 Correctness + Integrity ✅ DONE
Goal: fix logic bugs, add constraints + migrations.

Auth correctness:
- [x] Signup: read real confirm field (`new_passw_second`), reject mismatch/duplicates with `flash` (`routes.py:signup_page`)
- [x] Unify guest checks into `GUEST_EMAIL` + `_is_guest()`/`_guest_blocked()`; guest blocked on trip/event/pic create, update, delete
- [x] `Riders.passw String(50)` → `String(255)` (hash truncation); `Riders.__init__(email)` (dropped ignored arg)
- [x] `get_id()` → numeric `id`; `load_user` by `id` with email fallback for old sessions

DB integrity:
- [x] FKs: `added_by`/`event_owner`/`pic_owner` → `Users_Tab.email`, `nullable=False`, indexed
- [x] Constraints: unique `(owner, name)` on trips/events (`uq_trips_owner_name`, `uq_events_owner_name`); `nullable=False` on owner/name/email; duplicate create/rename handled with `flash` (no 500)
- [x] Cascade in `delete_user` extended to `TripPicture` (was leaking pics)
- [x] Flask-Migrate 2.7.0 wired (`requirements.txt`, `init_app`); `db.create_all()` removed; `migrations/` with initial revision `3f8a1c2d4e5b`; `Procfile` → `flask db upgrade && gunicorn app:app`

Acceptance (verified on temp copies, committed DB untouched):
- [x] Fresh DB: `flask db upgrade` creates full schema (FKs, VARCHAR(255), uniques, indexes, version stamped)
- [x] Existing DB: `flask db stamp head` path verified; all Phase 1 checks still green
- [x] Signup mismatch/duplicate → form + flash, no user/dup; session stores numeric id; guest writes uniformly blocked; admin user-delete cascades trips+events+pics

Note: `view_trips` / `view_mechanical_ev` don't render flashes, so guest-delete feedback
is silent there — consider adding flash blocks (Phase 3 polish).

## Phase 3 — Hardening + Structure ✅ DONE
Goal: defense in depth + maintainability.

- [x] Single auth source: `application/helpers.py` (`current_email()` from `current_user`); all `session['logged_user']` reads/writes removed; `is_admin()` / `admin_required` / `owner_required(model, owner, id, missing_as_404)` (+ `g.row`) replace per-route boilerplate
- [x] Deletes → `POST` only (`delete_trip`, `delete_event`, `delete_user`; GET → `405`); CSRF via `Flask-WTF==0.14.3`/`WTForms==2.3.3` (`CSRFProtect`, token in every POST form, delete links converted to forms)
- [x] Login rate-limit: hand-rolled `components/rate_limit.py` (5 fails / 5 min / IP → `429`); password min-length 8 on signup; `SECRET_KEY` fail-fast in `init_app`
- [x] `components/exporter.py`: ORM → `to_csv()` string; `download_file` streams `BytesIO` via `send_file` (Flask 1.x/2+ compatible) — no temp files, no `os.remove` race, CWD-independent
- [x] `routes.py` (~400 lines) split into blueprints: `auth`, `main`, `trips`, `events`, `pics`, `admin` (+ `helpers`); `LoginManager` with `login_view` moved to `__init__.py`; templates re-pointed to qualified endpoints, `home` passes full `crr_email` (fixes `user_panel` link)
- [x] Flash blocks added to `view_trips` / `view_mechanical_ev` (Phase 2 note resolved)

Acceptance (verified on temp copies, committed DB untouched):
- [x] No `GET` deletes (`405`); POST without CSRF → `400`; anon → redirect to login (`?next=`)
- [x] No temp CSV leftovers (pre-existing `temp_files/data_*.csv` untouched); export returns `text/csv` with ORM column order
- [x] Full route sweep: 21 rules, all Phase 1/2 checks green (owner `200`, cross-owner `403`/`404`, guest blocked, admin cascade incl. pics); 6th bad login → `429`

---

## Frontend — UX + Performance ⬜ PENDING
Goal: template-level quick wins first (Jinja SSR, Bootstrap cards, base64-inline pics,
unbounded lists), then data flow, then platform — each gated by Locust numbers.
Context: findings in `ui-errors/ux-review.md`; load method per skill-locust
(latency → stress at 1/10/100/1000 users → timestamped `metrics/metrics.md`).

### Frontend Phase 1 — Template-only quick wins ✅ DONE
UX:
- [x] Delete confirmations (`confirm()`) on all POST delete forms (detail ×2, admin ×3, account)
- [x] Custom error pages (`403/404/405/429/500.html`) with home link + retry hint for `429`, wired in `init_app`
- [x] Fix typos ("KM Intial", "No KM - Intiial"); login prefill replaced with explicit "Try the demo account" button

Performance:
- [x] Pagination (12/page, newest first, clamped) on `view_trips` / `view_mechanical_ev` / `view_trip_pics` via shared `helpers.paginate_query`
- [x] `loading="lazy"` on home + pics images; pics page capped by pagination

Acceptance (verified on temp DB):
- [x] Custom 404/405 bodies; pager `Page 1 of 2`, clamp `?page=99` → last page; no prefilled login values

### Frontend Phase 2 — Template + data flow ✅ DONE
UX:
- [x] Read-only detail cards with explicit "Edit" toggle (edit forms hidden until toggled) on trip + event pages
- [x] Pic upload enabled: extension allowlist, 5 MB cap, PIL validity check, inline guidelines note (button no longer disabled)
- [x] Guest story: read-only demo banner on home linking to signup
- [x] `human_date` Jinja filter (`01 Jan 2024`) used on detail pages; search (`?q=`, owner-scoped `ilike`) on trips + events lists; responsive (`.table-responsive`) admin tables

Performance:
- [x] Thumbnail pipeline: `TripPicture.pic_preview` (migration `7c2d9a1b4f6e`, defensive `has_column` guards) generated at upload via revived `PicFormatter.get_resized_pic` (Pillow 8/10+ compatible resampling)
- [x] `/pic/<id>/<thumb|full>` route with `Cache-Control: public, max-age=86400`, owner-checked; legacy rows backfilled lazily; list page uses `<img src>` (no more inline base64 — 4.2 KB HTML)

Acceptance (verified on temp copies, committed DB untouched):
- [x] Fresh `upgrade` runs both revisions; legacy DB path `stamp 3f8a1c2d4e5b && upgrade` adds the column; legacy thumb 200 + persisted
- [x] Bad upload/extension blocked with flash, no rows; thumb/full/cache headers verified; search hit/miss; read-only detail + toggle + human date

### Frontend Phase 3 — Platform (only if numbers demand it) ⬜ PENDING
- [ ] Mobile-responsiveness pass once layout is stable
- [ ] gunicorn + Postgres to escape the dev-server/SQLite-lock ceiling; static-asset
  caching/versioning; final Locust run (up to 1000 users) to quantify end-state

---

## Progress log
| Date | Event |
|------|-------|
| 2026-10-16 | Phases 0–1 implemented + verified on temp DB copy |
| 2026-10-16 | Phase 2 implemented + verified (fresh `upgrade` + existing-data `stamp` + regression) |
| 2026-10-16 | Phase 3 implemented + verified (blueprints, CSRF, POST deletes, streaming export) |
| 2026-10-16 | Playwright UI walkthrough (skill-playwright): 43/43 green; fixed `view_trip_pics` stale endpoint; reports in `ui-errors/` |
| 2026-10-16 | Formatter pass (skill-formatter): ruff/black/mypy clean, 71 defs annotated, `pyproject.toml` pins py37; log in `formating/formatting.md` |
| | All phases complete |

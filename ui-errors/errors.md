# UI Errors — Playwright walkthrough (2026-10-16)

Harness: `/tmp/opencode/ui_walkthrough.py` (Playwright + Chromium headless) against the
app booted from repo root on an isolated DB copy (`/tmp/opencode/phase3ui.sqlite3`;
committed `application/tripsDB.sqlite3` untouched). Final result: **43/43 checks pass**.

## Real bugs found (all fixed)

1. **`view_trip_pics.html` 500 — stale blueprint endpoint (FIXED)**
   - Symptom: `GET /view_trip_pics` → 500, `BuildError: Could not build url for
     endpoint 'download_file' … Did you mean 'main.download_file'?`
   - Cause: Phase 3 blueprint rename missed one `url_for('download_file', …)` on
     `application/templates/view_trip_pics.html:36` (disabled Download button).
     The earlier grep only matched endpoints followed by a quote/comma, so
     `url_for( 'download_file', tab=…)` slipped through.
   - Fix: qualified to `main.download_file`; re-swept all templates with a looser
     pattern — no other misses (`static` references are fine).
   - Lesson: endpoint renames need a render-every-template sweep, not just grep
     for exact call shapes. The walkthrough now visits every page, which is what
     caught this.

## Non-issues (investigated, no fix needed)

- `GET /delete_trip/<id>` → 405, POST without CSRF → 400, `/trip/<other-id>` → 404,
  `/download/nope` → 404: all deliberate negative probes, all behave as designed.
- Console "Failed to load resource" lines during the run correspond exactly to those
  deliberate probes. No JS exceptions, no 5xx in any run after the fix above.
- `anon /home` lands on `/?next=%2Fhome` (Flask-Login `login_view`), not bare `/` —
  assertion adjusted; behavior is correct.
- Admin-panel `delete_user` form action is `/delete/<email>` (no `delete_user` string
  in the URL) — test selector fixed to `form[action*="/delete/"]`; app is fine.

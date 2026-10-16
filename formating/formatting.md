# Formatting & typing pass (2026-10-16)

Tools: ruff 0.17.1, black 26.10.1, mypy 2.4.0. Scope: hand-written sources only
(`app.py`, `config.py`, `application/*.py`, `components/*.py`, `migrations/env.py`,
`migrations/versions/*`). Excluded: `__pycache__`, venvs, `alembic.ini`,
`script.py.mako`, templates, `/tmp` harnesses. Verified after: full gate re-run +
fresh-DB smoke test (signup → login → trip CRUD → CSV export), all green.

## ruff check — 0 remaining (started at 22)
- Auto-fixed (safe): import sorting (I001), `(object)` bases (UP004), stray parens
  (UP034), `__future__.with_statement` (UP010), dup/unused imports (F811/F401 —
  a leftover local `is_admin` import in `admin.py`).
- Manual (equivalent, behavior-identical): `%`-format → f-strings (UP031 ×5),
  `PORT` default `5000` → `'5000'` (PLW1508).
- New `pyproject.toml`: `target-version = "py37"` (pinned runtime, see
  `runtime.txt`) + `ignore = ["FA100"]` (codebase deliberately uses
  `typing.Optional/List/Dict/Union`, valid on every interpreter).

## black + ruff format — clean
18 files normalized (quotes, spacing, line breaks). No logic touched.

## mypy — 0 errors, incl. `--disallow-untyped-defs` (was 71 untyped defs + 6 errors)
- Annotated all 71 defs with py3.7-safe `typing` hints (views → `Union[str, Response]`
  with werkzeug `Response`, which is what `redirect()` returns on Flask 1.x and 2+/3.x).
- `helpers.require_email()` added: assert-backed `str` accessor for `@login_required`
  views (replaces `Optional` juggling at 16 call sites, zero runtime effect when logged in).
- `events.py` now coerces `event_km`/`event_cost` with `int()`/`float()`, matching the
  existing `trips.py` pattern.
- 6 targeted `type: ignore`s, all documented in code: `db.Model` bases (dynamic on
  Flask-SQLAlchemy), Flask-1.x `attachment_filename` compat shim, Pillow
  `Image.NEAREST` (exists on pinned Pillow 8, moved in Pillow 10+), decorator `wrapper`
  returns.
- Impossible-state `assert`s added in `riderProfile` (DB handles set before use) and
  `migrations/env.py` (alembic always provides config values).

## Incident during the pass
Default ruff rewrote new hints to `X | Y` / builtin generics (fatal on Python ≤3.9 at
import time). Reverted all 13 spots to `typing` forms and pinned `target-version`.
Lesson: always run formatters with the project's pinned interpreter target.

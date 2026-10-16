# UX Summary + Improvement Plan (2026-10-16)

Based on a scripted Playwright walkthrough of every route (guest, regular, admin).

## What works well

- Core flows are complete and consistent: login → home cards → create → list → detail → update → delete, for trips, events, and pics.
- Auth feedback is clear: wrong-password flash, signup mismatch/duplicate/short-password flashes, guest-write flashes, `?next=` redirect after login.
- Security posture is visible in the UI: deletes are buttons in POST forms (noCSRF-less links), CSRF tokens in every form, 405 on GET deletes.
- CSV export downloads with proper filenames and correct column order.

## Pain points observed

1. **Guest is a dead end with demo data it can't touch.** Guest owns example trips/events/pics but every write (including delete of its own rows) is blocked with "can't save data as Guest". A first-time visitor can't try the edit flow at all.
2. **No confirmation on destructive actions.** DELETE submits immediately — one misclick wipes a trip/event/account. No undo.
3. **Pic upload is disabled** (`trip_pics.html`: submit button `disabled` "until community guidelines are created") yet the form and nav still advertise it.
4. **Detail pages double as edit forms** with no read-only view; the UPDATE/DELETE buttons sit side by side, easy to mis-tap.
5. **Error pages are bare** (default 403/404/405/429) — no link back home, no explanation (e.g. 429 gives no "try again in X").
6. **Timestamps/dates render raw** (`2024-06-01`, `pic_posted_on` unused in lists); lists have no search, sort, or pagination — fine at this scale, will degrade.
7. **Inconsistent labels/typos**: "KM Intial", "No KM - Intiial", "Mechanical Events" vs "mechanical operations", event detail hack remnants gone but `$` convention lingers nowhere — good, keep it that way.
8. **Login form ships with guest credentials prefilled** (`guest@guest.com` / `123`) — convenient for demo, bad habit for production.
9. **Mobile layout**: fixed `min-width: 380px` containers will overflow small screens; tables in admin panel have no responsive wrapper.

## Improvement plan (proposed, prioritized)

- **P1 — safety**: JS `confirm()` (or modal) on all DELETE forms; read-only detail view with explicit "Edit" toggle.
- **P1 — guest story**: either make guest read-only *without* seeded writable-looking data, or add a "demo mode" sandbox (separate throwaway account whose data resets).
- **P2 — errors**: custom `403/404/429/500` pages with home link + (for 429) retry hint.
- **P2 — pics**: either enable upload with validation + guidelines page, or hide the dead nav/form until then.
- **P3 — polish**: fix typos, unify terminology, humanize dates, responsive tables/containers, remove prefilled login credentials, add list search/sort when rows grow.

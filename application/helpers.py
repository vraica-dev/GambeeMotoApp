"""Shared auth/authorization helpers (single source of truth for identity).

Identity comes ONLY from Flask-Login's ``current_user`` -- no custom
``session['logged_user']`` keys are used anywhere.
"""

from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from flask import abort, current_app, flash, g, redirect, url_for
from flask_login import current_user, login_required

GUEST_EMAIL = "guest@guest.com"

F = TypeVar("F", bound=Callable[..., Any])


def current_email() -> Optional[str]:
    if current_user.is_authenticated:
        return current_user.email
    return None


def require_email() -> str:
    """Current user's email; only valid behind @login_required."""
    email = current_email()
    assert email is not None, "require_email() used without authenticated user"
    return email


def paginate_query(
    query: Any, page: int, per_page: int = 12
) -> Tuple[List[Any], int, int]:
    """Newest-agnostic slice of an ordered query; clamps out-of-range pages."""
    page = max(page, 1)
    total = query.count()
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(page, pages)
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, page, pages


def is_admin(email: Optional[str] = None) -> bool:
    return (email if email is not None else current_email()) == current_app.config[
        "ADMIN_USER"
    ]


def is_guest() -> bool:
    return current_email() == GUEST_EMAIL


def guest_blocked(action: str = "save") -> bool:
    if is_guest():
        flash(f"Sorry. You can't {action} data as Guest.")
        return True
    return False


def admin_required(view: F) -> F:
    @wraps(view)
    @login_required
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not is_admin():
            return redirect(url_for("auth.login_page"))
        return view(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def owner_required(
    model: Any, owner_attr: str, id_kwarg: str, missing_as_404: bool = False
) -> Callable[[F], F]:
    """Load row by id, enforce owner-or-admin. Row is exposed as ``g.row``.

    ``missing_as_404``: use 404 (detail views, avoids enumeration) instead of
    403 when the row exists but belongs to someone else.
    """

    def decorator(view: F) -> F:
        @wraps(view)
        @login_required
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            row = model.query.filter_by(id=kwargs[id_kwarg]).first()
            if row is None:
                abort(404)
            if not is_admin() and getattr(row, owner_attr) != current_email():
                abort(404 if missing_as_404 else 403)
            g.row = row
            return view(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator

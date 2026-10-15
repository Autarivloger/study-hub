import hmac
import re
import secrets
from flask import abort,session


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"]=secrets.token_urlsafe(24)
    return session["csrf_token"]


def check_csrf(request):
    if request.method=="POST":
        expected=session.get("csrf_token")
        supplied=request.form.get("csrf_token","")
        if not isinstance(expected,str) or len(supplied)>128 or not supplied.isascii() or not hmac.compare_digest(expected,supplied):
            abort(400,description="Form token missing or stale. Reload this form.")


def username_value(raw):
    value=raw.strip().lower()
    return value if re.fullmatch(r"[a-z0-9_]{3,32}",value) else None


def post_value(raw,limit):
    value=raw.strip()
    if not 1<=len(value)<=limit or "\x00" in value:
        return None
    return value

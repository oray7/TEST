import hmac
import hashlib
import os
import sys

SECRET = "ch4ng3-th1s-t0-s0m3th1ng-0nly-y0u-kn0w"

def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _key_path():
    return os.path.join(_app_dir(), "license.key")

def _valid(key):
    raw = key.replace("-", "").lower()
    if len(raw) != 16:
        return False
    token, sig = raw[:8], raw[8:]
    expected = hmac.new(SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:8]
    return hmac.compare_digest(sig, expected)

def check_license():
    path = _key_path()
    if not os.path.exists(path):
        return False
    with open(path) as f:
        return _valid(f.read().strip())

def activate(key):
    if _valid(key):
        with open(_key_path(), "w") as f:
            f.write(key.strip())
        return True
    return False

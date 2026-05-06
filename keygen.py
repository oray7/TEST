import hmac
import hashlib
import secrets
import json
import os
from datetime import datetime

SECRET = "ch4ng3-th1s-t0-s0m3th1ng-0nly-y0u-kn0w"
KEYS_FILE = "keys.json"

def _generate():
    token = secrets.token_hex(4)
    sig = hmac.new(SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:8]
    raw = (token + sig).upper()
    return "-".join(raw[i:i+4] for i in range(0, 16, 4))

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE) as f:
            return json.load(f)
    return []

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2, ensure_ascii=False)

def generate_key(note=""):
    key = _generate()
    keys = load_keys()
    keys.append({
        "key": key,
        "note": note,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "active"
    })
    save_keys(keys)
    return key

if __name__ == "__main__":
    count = int(input("How many keys? "))
    note = input("Note (customer name or leave empty): ").strip()
    for _ in range(count):
        key = generate_key(note)
        print(key)

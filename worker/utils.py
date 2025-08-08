import json


def parse_config(raw):
    if raw is None:
        return {}
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="replace")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    # Handle the double-encoded case: obj is a JSON string
    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except json.JSONDecodeError:
            return {}

    return obj if isinstance(obj, dict) else {}
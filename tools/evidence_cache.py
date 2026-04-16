# tools/evidence_cache.py
"""Content-addressed evidence cache.

Keys: sha256(normalized_query + '|' + url). Entries stored as <key>.json
in a caller-supplied cache directory (typically assets/.forge-cache/).
LRU eviction by mtime. Reads do NOT mutate the file — mtime reflects
last-write only, ensuring deterministic LRU ordering under parallel dispatch.
"""
import hashlib
import json
import os
import re
import tempfile


def normalize_query(q):
    """Lowercase, strip punctuation, collapse whitespace."""
    q = q.lower()
    q = re.sub(r"[^\w\s]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q


def make_key(query, url):
    payload = normalize_query(query) + "|" + (url or "")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _path(cache_dir, key):
    return os.path.join(cache_dir, f"{key}.json")


def read_cache(cache_dir, key):
    """Return the cache entry (dict) or None.

    Tolerates corrupt cache entries (returns None) and missing files.
    Does NOT mutate the entry on read — mtime-based LRU relies on
    mtime reflecting last-write, not last-read. Hit counts are lost
    (telemetry, not load-bearing).
    """
    p = _path(cache_dir, key)
    if not os.path.isfile(p):
        return None
    try:
        with open(p) as f:
            entry = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    return entry


def write_cache(cache_dir, key, entry):
    """Atomically write a cache entry (safe under concurrent writers).

    Writes to a sibling .tmp file then os.replace() to the final path —
    atomic on POSIX. Prevents torn reads under parallel subagent dispatch.
    """
    os.makedirs(cache_dir, exist_ok=True)
    _atomic_write(_path(cache_dir, key), entry)


def _atomic_write(path, entry):
    """Write JSON atomically: temp-file + rename."""
    cache_dir = os.path.dirname(path) or "."
    # Stem comes from the final filename (keeps tmp discoverable if interrupted)
    stem = os.path.basename(path).rsplit(".", 1)[0]
    fd, tmp = tempfile.mkstemp(dir=cache_dir, prefix=f".{stem}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(entry, f)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise


def cache_stats(cache_dir):
    if not os.path.isdir(cache_dir):
        return {"entries": 0, "size_bytes": 0}
    total = 0
    count = 0
    for f in os.listdir(cache_dir):
        if f.endswith(".json"):
            count += 1
            total += os.path.getsize(os.path.join(cache_dir, f))
    return {"entries": count, "size_bytes": total}


def evict_lru(cache_dir, keep):
    """Keep the N most-recently-used entries, delete the rest. Returns evicted keys."""
    files = [
        (f[:-5], os.path.getmtime(os.path.join(cache_dir, f)))
        for f in os.listdir(cache_dir) if f.endswith(".json")
    ]
    files.sort(key=lambda x: x[1])  # oldest first
    to_evict = files[:-keep] if len(files) > keep else []
    evicted_keys = []
    for key, _ in to_evict:
        os.remove(os.path.join(cache_dir, f"{key}.json"))
        evicted_keys.append(key)
    return evicted_keys

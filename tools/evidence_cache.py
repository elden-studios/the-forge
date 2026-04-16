# tools/evidence_cache.py
"""Content-addressed evidence cache.

Keys: sha256(normalized_query + '|' + url). Entries stored as <key>.json
in a caller-supplied cache directory (typically assets/.forge-cache/).
Reads auto-increment 'hits'. LRU eviction by mtime.
"""
import hashlib
import json
import os
import re


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
    """Return the cache entry (dict) or None. Auto-increments 'hits'."""
    p = _path(cache_dir, key)
    if not os.path.isfile(p):
        return None
    with open(p) as f:
        entry = json.load(f)
    entry["hits"] = entry.get("hits", 0) + 1
    with open(p, "w") as f:
        json.dump(entry, f)
    return entry


def write_cache(cache_dir, key, entry):
    os.makedirs(cache_dir, exist_ok=True)
    with open(_path(cache_dir, key), "w") as f:
        json.dump(entry, f)


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

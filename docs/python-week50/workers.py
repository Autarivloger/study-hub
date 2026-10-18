"""Importable, deterministic CPU workers for spawn-based teaching examples."""

import os

CHILD_COUNTER = 0


def square(value):
    return value * value


def child_increment():
    global CHILD_COUNTER
    CHILD_COUNTER += 1
    return CHILD_COUNTER


def process_identity(value):
    return {"value": value * value, "pid": os.getpid()}


def fail_job(message):
    raise ValueError(message)


def emit_square(value, queue):
    queue.put(value * value)


def increment_shared(shared, count):
    for _ in range(count):
        with shared.get_lock():
            shared.value += 1


def score_payload(payload, rounds=20_000):
    """Pure Python arithmetic; not a native hash kernel that releases the GIL."""
    if type(rounds) is not int or not 0 <= rounds <= 2_000_000:
        raise ValueError("rounds must be an integer from 0 to 2000000")
    if set(payload) != {"id", "value"}:
        raise ValueError("payload needs exactly id and value")
    if any(type(payload[name]) is not int or payload[name] < 0 for name in ["id", "value"]):
        raise ValueError("payload values must be nonnegative ordinary integers")
    total = payload["value"] % 1_000_003
    for index in range(rounds):
        total = (total + ((index ^ payload["value"]) * 31)) % 1_000_003
    return {"id": payload["id"], "score": total}

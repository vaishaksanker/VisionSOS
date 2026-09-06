import threading


_lock = threading.Lock()

_current_state = "NORMAL"
_current_countdown = None
_last_event = None
_system_active = True


def write_status(state, countdown=None):
    global _current_state, _current_countdown

    with _lock:
        _current_state = state
        _current_countdown = countdown


def write_event(event_result):
    global _last_event

    with _lock:
        _last_event = event_result


def read_state():
    with _lock:
        return {
            "state": _current_state,
            "countdown": _current_countdown,
            "last_event": _last_event,
            "system": "ACTIVE" if _system_active else "OFFLINE"
        }


def set_system_active(active):
    global _system_active

    with _lock:
        _system_active = active
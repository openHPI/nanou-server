from datetime import datetime

WATCHED_DEFAULT_PROPS = {
    'date': datetime.min.isoformat(),
    'rating': -1,
    'progress': 0,
}

PREFERENCE_DEFAULT_PROPS = {
    'weight': 0.5,
}

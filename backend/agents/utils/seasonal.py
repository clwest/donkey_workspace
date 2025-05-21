from datetime import datetime


def get_current_season() -> str:
    now = datetime.now()
    if now.month in [3, 4, 5]:
        return "spring"
    if now.month in [6, 7, 8]:
        return "summer"
    if now.month in [9, 10, 11]:
        return "fall"
    return "winter"

from datetime import datetime
from App import constants

def maybe_datetime_to_display_string(d: datetime | None) -> str:
    if not d:
        return ''
    return d.strftime(constants._DATE_TIME_DISPLAY_FORMAT)
from datetime import datetime
from App import constants

def create_safe_file_name(title: str, audio_only: bool) -> str:
    ext = '.mp3' if audio_only else '.mp4'

    # TODO this is a niavie way to do this, need to find a better way.
    new_title = title.replace(' ', '_') \
                .replace("'", '') \
                .replace('"', '') \
                .replace('&', 'and') \
                .replace('(', '') \
                .replace(')', '') \
                .replace('<', '') \
                .replace('>', '') \
                .replace('?', '') \
                .replace(';', '') \
                .replace(':', '') \
                .replace(',', '') \
                .replace('{', '') \
                .replace('}', '') \
                .replace('|', '') \
                .replace('/', '') \
                .replace('/', '') \
                .replace('~', '') \
                .replace('`', '') \
                .replace('$', '') \
                .replace('*', '') \
                .replace('^', '') \
                .replace('\b', '') \
                .replace('!', '') \
                .replace('@', '') \
                .replace('#', '') \
                .replace('%', '')


    return f"{new_title}{ext}"

def maybe_datetime_to_display_string(d: datetime | None) -> str:
    if not d:
        return ''
    return d.strftime(constants._DATE_TIME_DISPLAY_FORMAT)
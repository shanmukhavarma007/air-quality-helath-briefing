import re
import html


def sanitize_string(value: str, max_length: int = 255) -> str:
    value = html.escape(value.strip())
    value = re.sub(r'\s+', ' ', value)
    return value[:max_length]


def sanitize_coordinates(lat: float, lon: float) -> tuple[float, float]:
    lat = max(-90.0, min(90.0, lat))
    lon = max(-180.0, min(180.0, lon))
    return round(lat, 6), round(lon, 6)


def sanitize_email(email: str) -> str:
    email = email.strip().lower()
    if not re.match(r'^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$', email):
        raise ValueError("Invalid email format")
    return email[:255]

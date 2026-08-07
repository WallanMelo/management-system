from datetime import datetime


def google_datetime(valor: str | None):

    if valor is None:
        return None

    return datetime.fromisoformat(
        valor.replace("Z", "+00:00")
    )
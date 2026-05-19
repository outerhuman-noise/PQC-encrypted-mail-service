import base64


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def unb64(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))

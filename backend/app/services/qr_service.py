import io
import uuid

import qrcode


def create_qr_token() -> str:
    """Create the single persistent token used by an application's QR record."""
    return uuid.uuid4().hex


def encode_qr_png(payload: str) -> bytes:
    """Encode the supplied tracking URL/payload as a PNG QR image."""
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_qr_payload(payload: str):
    """Backward-compatible helper: create a token and encode the payload."""
    token = create_qr_token()
    return token, encode_qr_png(payload)

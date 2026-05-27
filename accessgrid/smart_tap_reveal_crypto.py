"""Internal crypto helpers for the SmartTap reveal flow.

Driven by Console.reveal_smart_tap; not part of the public SDK surface.
Uses ``cryptography`` for ECDH + HKDF-SHA256 + AES-256-GCM.
"""

import base64

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .client import DecryptError, InvalidEnvelopeError

_HKDF_INFO = b"accessgrid-smart-tap-reveal-v1"


def generate_keypair():
    """Generate a fresh ephemeral P-256 keypair for a reveal call.

    Returns a dict ``{"private_key": <EllipticCurvePrivateKey>,
    "public_key_pem": <str>}``. The PEM is SubjectPublicKeyInfo, ready to
    submit as ``client_public_key``.
    """
    priv = ec.generate_private_key(ec.SECP256R1())
    pub_pem = (
        priv.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("ascii")
    )
    return {"private_key": priv, "public_key_pem": pub_pem}


def decrypt_envelope(envelope, private_key):
    """Decrypt the ``encrypted_private_key`` envelope from the reveal endpoint.

    Performs ECDH + HKDF-SHA256 + AES-256-GCM, matching the server-side
    encryption parameters exactly. Returns the plaintext SmartTap key PEM
    as a string.

    Raises ``InvalidEnvelopeError`` on missing/bad envelope fields,
    ``DecryptError`` on AES-GCM auth-tag verification failure.
    """
    pem = (envelope or {}).get("ephemeral_public_key")
    if not isinstance(pem, str) or not pem.strip():
        raise InvalidEnvelopeError("Invalid ephemeral_public_key in envelope")

    try:
        server_pub = serialization.load_pem_public_key(pem.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise InvalidEnvelopeError("Invalid ephemeral_public_key in envelope") from exc

    iv = _decode_b64(envelope.get("iv"), "iv")
    ciphertext = _decode_b64(envelope.get("ciphertext"), "ciphertext")
    tag = _decode_b64(envelope.get("tag"), "tag")

    shared_secret = private_key.exchange(ec.ECDH(), server_pub)
    aes_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"",
        info=_HKDF_INFO,
    ).derive(shared_secret)

    try:
        plaintext = AESGCM(aes_key).decrypt(iv, ciphertext + tag, b"")
    except InvalidTag as exc:
        raise DecryptError("AES-GCM decryption failed (auth tag verification)") from exc

    return plaintext.decode("utf-8")


def _decode_b64(value, field_name):
    if not isinstance(value, str):
        raise InvalidEnvelopeError(f"Envelope {field_name} must be base64-encoded")
    try:
        return base64.b64decode(value, validate=True)
    except (base64.binascii.Error, ValueError) as exc:
        raise InvalidEnvelopeError(
            f"Envelope {field_name} must be base64-encoded"
        ) from exc

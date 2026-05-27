"""Tests for the SmartTap reveal flow.

Uses a captured wire-compat fixture (same envelope + caller keypair used in
Ruby / Elixir / JS / Java / PHP specs). caller_private_key is ephemeral and
single-use by design (the server rejects reuse on pubkey fingerprint), so
committing it carries no credential risk.
"""

import base64

import pytest
from cryptography.hazmat.primitives import serialization

from accessgrid import (
    DecryptError,
    InvalidEnvelopeError,
    PublishTemplateResponse,
    RevealTemplatePrivateKey,
)
from accessgrid.smart_tap_reveal_crypto import (
    decrypt_envelope,
    generate_keypair,
)

FIXTURE_CALLER_PRIVATE_KEY_PEM = (
    "-----BEGIN EC PRIVATE KEY-----\n"
    "MHcCAQEEIIou+Kk08kWAjhi0WyIx+L2GrgStGBCPODlwKYKd5BydoAoGCCqGSM49\n"
    "AwEHoUQDQgAE+gnDxXJt1SBaCK8roKH8QvOa/ItdQUe85JIsUc6RvhD/udLaFtHY\n"
    "m+MnOmeSdVaKTPWudH0+iGbleB3kS7lYxQ==\n"
    "-----END EC PRIVATE KEY-----\n"
)

FIXTURE_ENVELOPE = {
    "alg": "ECDH-ES+A256GCM",
    "ephemeral_public_key": (
        "-----BEGIN PUBLIC KEY-----\n"
        "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7mg6i99GcIVutMPr/PXSBSQVlbLM\n"
        "tnJO10ZBjk9ZTfw6wwAVNBnDBiqY7VrdOG1JdFOYoac+NkAlyMRGYk2tVQ==\n"
        "-----END PUBLIC KEY-----\n"
    ),
    "iv": "5X2OCht+kLB/xQmX",
    "ciphertext": "ckYyA3FdRYjOFI/FKz/QeR5Yf9nZZFzo73kDXKZSB/EgbQ==",
    "tag": "0vwkjVaCwi5zl37xvJPxeg==",
}

FIXTURE_EXPECTED_PLAINTEXT = "FIXTURE-PLAINTEXT-NOT-A-CREDENTIAL"


@pytest.fixture
def fixture_private_key():
    return serialization.load_pem_private_key(
        FIXTURE_CALLER_PRIVATE_KEY_PEM.encode("ascii"),
        password=None,
    )


class TestDecryptEnvelope:
    def test_decrypts_captured_server_envelope(self, fixture_private_key):
        assert (
            decrypt_envelope(FIXTURE_ENVELOPE, fixture_private_key)
            == FIXTURE_EXPECTED_PLAINTEXT
        )

    def test_tampered_tag_raises_decrypt_error(self, fixture_private_key):
        raw_tag = bytearray(base64.b64decode(FIXTURE_ENVELOPE["tag"]))
        raw_tag[0] ^= 0x01
        tampered = {
            **FIXTURE_ENVELOPE,
            "tag": base64.b64encode(bytes(raw_tag)).decode("ascii"),
        }

        with pytest.raises(DecryptError, match="AES-GCM decryption failed"):
            decrypt_envelope(tampered, fixture_private_key)

    def test_wrong_private_key_raises_decrypt_error(self):
        wrong = generate_keypair()["private_key"]

        with pytest.raises(DecryptError):
            decrypt_envelope(FIXTURE_ENVELOPE, wrong)

    def test_missing_ephemeral_pubkey_raises_invalid_envelope(
        self, fixture_private_key
    ):
        envelope = {
            k: v for k, v in FIXTURE_ENVELOPE.items() if k != "ephemeral_public_key"
        }

        with pytest.raises(InvalidEnvelopeError, match="ephemeral_public_key"):
            decrypt_envelope(envelope, fixture_private_key)

    def test_non_base64_iv_raises_invalid_envelope(self, fixture_private_key):
        bad = {**FIXTURE_ENVELOPE, "iv": "not!base64!"}

        with pytest.raises(InvalidEnvelopeError, match="base64"):
            decrypt_envelope(bad, fixture_private_key)


class TestGenerateKeypair:
    def test_returns_private_key_and_public_pem(self):
        result = generate_keypair()
        assert "private_key" in result
        assert "public_key_pem" in result
        assert result["public_key_pem"].startswith("-----BEGIN PUBLIC KEY-----")

    def test_each_call_returns_distinct_keypair(self):
        a = generate_keypair()
        b = generate_keypair()
        assert a["public_key_pem"] != b["public_key_pem"]


class TestPublishTemplateResponse:
    def test_maps_wire_fields(self):
        result = PublishTemplateResponse({"id": "tmpl-42", "status": "in-review"})
        assert result.id == "tmpl-42"
        assert result.status == "in-review"


class TestRevealTemplatePrivateKey:
    def test_maps_snake_case_wire_fields(self):
        result = RevealTemplatePrivateKey(
            {
                "key_version": "tmpl-42",
                "collector_id": "12345678",
                "fingerprint": "sha256:deadbeef",
                "private_key": FIXTURE_EXPECTED_PLAINTEXT,
            }
        )
        assert result.key_version == "tmpl-42"
        assert result.collector_id == "12345678"
        assert result.fingerprint == "sha256:deadbeef"
        assert result.private_key == FIXTURE_EXPECTED_PLAINTEXT

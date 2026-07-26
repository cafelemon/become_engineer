from __future__ import annotations

import contextlib
import io
import unittest

from delivery_cli import (
    DeliveryError,
    ProviderConfig,
    ScriptedTransport,
    audit_event,
    invoke_provider,
    load_config,
    main,
    offline_evidence,
    redact,
    require_real_call_opt_in,
)


class DeliveryCliTests(unittest.TestCase):
    def test_offline_is_default_and_needs_no_secret(self) -> None:
        config = load_config({})
        self.assertEqual((config.mode, config.provider), ("offline", "scripted"))
        self.assertNotIn("api_key", repr(config).lower())

    def test_provider_mode_fails_closed_on_config_and_secret(self) -> None:
        with self.assertRaises(DeliveryError) as caught:
            load_config({"MODEL_MODE": "provider", "MODEL_PROVIDER": "demo"})
        self.assertEqual(caught.exception.code, "invalid_config")
        with self.assertRaises(DeliveryError) as caught:
            load_config({
                "MODEL_MODE": "provider",
                "MODEL_PROVIDER": "demo",
                "MODEL_BASE_URL": "https://example.invalid/v1/responses",
            })
        self.assertEqual(caught.exception.code, "missing_secret")

    def test_provider_requires_https_and_bounded_timeout(self) -> None:
        base = {
            "MODEL_MODE": "provider",
            "MODEL_PROVIDER": "demo",
            "MODEL_API_KEY": "synthetic",
        }
        for updates in [
            {"MODEL_BASE_URL": "http://example.invalid"},
            {"MODEL_BASE_URL": "https://example.invalid", "MODEL_TIMEOUT_SECONDS": "0"},
            {"MODEL_BASE_URL": "https://example.invalid", "MODEL_TIMEOUT_SECONDS": "many"},
        ]:
            with self.subTest(updates=updates), self.assertRaises(DeliveryError):
                load_config(base | updates)

    def test_real_call_requires_two_independent_gates(self) -> None:
        for cli_real, gate in [(False, "1"), (True, "0"), (True, "")]:
            with self.subTest(cli_real=cli_real, gate=gate), self.assertRaises(DeliveryError) as caught:
                require_real_call_opt_in({"ALLOW_REAL_PROVIDER": gate}, cli_real)
            self.assertEqual(caught.exception.code, "real_call_not_enabled")
        require_real_call_opt_in({"ALLOW_REAL_PROVIDER": "1"}, True)

    def test_scripted_transport_receives_secret_but_audit_does_not(self) -> None:
        config = ProviderConfig(
            "provider", "demo", "model-v1", "https://example.invalid/v1/responses", 5
        )
        transport = ScriptedTransport()
        result = invoke_provider(config, {"MODEL_API_KEY": "synthetic-key"}, "hello", transport)
        self.assertEqual(transport.calls[0]["headers"]["Authorization"], "Bearer synthetic-key")
        audit = audit_event(config, result, 1)
        self.assertNotIn("synthetic-key", repr(audit))
        self.assertNotIn("hello", repr(audit))

    def test_recursive_redaction_covers_nested_sensitive_fields(self) -> None:
        value = {
            "Authorization": "Bearer secret",
            "nested": [{"token": "abc", "safe": "kept"}],
            "cookie": "session=secret",
        }
        cleaned = redact(value)
        self.assertEqual(cleaned["Authorization"], "[REDACTED]")
        self.assertEqual(cleaned["nested"][0]["token"], "[REDACTED]")
        self.assertEqual(cleaned["nested"][0]["safe"], "kept")
        self.assertNotIn("secret", repr(cleaned))

    def test_transport_exception_is_normalized_without_secret(self) -> None:
        config = ProviderConfig(
            "provider", "demo", "model-v1", "https://example.invalid/v1/responses", 5
        )
        with self.assertRaises(DeliveryError) as caught:
            invoke_provider(
                config,
                {"MODEL_API_KEY": "must-not-escape"},
                "hello",
                ScriptedTransport(fail=True),
            )
        self.assertEqual(caught.exception.code, "provider_call_failed")
        self.assertNotIn("must-not-escape", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_offline_cli_evidence_is_deterministic_and_network_free(self) -> None:
        evidence = offline_evidence()
        self.assertEqual(evidence, offline_evidence())
        self.assertNotIn("synthetic-test-secret", evidence)
        self.assertIn("network:disabled-by-default", evidence)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main([], {})
        self.assertEqual(status, 0)
        self.assertEqual(output.getvalue().strip(), evidence)


if __name__ == "__main__":
    unittest.main()

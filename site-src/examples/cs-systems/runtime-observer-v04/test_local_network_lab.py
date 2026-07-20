from __future__ import annotations

import unittest

from local_network_lab import HOST, run_http_exchange


class LocalNetworkLabTests(unittest.TestCase):
    def test_server_uses_loopback_and_an_ephemeral_port(self) -> None:
        result = run_http_exchange("/health")
        self.assertEqual(result.host, HOST)
        self.assertGreater(result.port, 0)
        self.assertTrue(result.connected)

    def test_http_success_and_not_found_remain_distinct(self) -> None:
        success = run_http_exchange("/health")
        missing = run_http_exchange("/missing")
        self.assertEqual((success.status, success.body), (200, '{"status":"ok"}'))
        self.assertEqual((missing.status, missing.body), (404, '{"error":"not_found"}'))

    def test_response_wait_produces_a_deterministic_client_timeout(self) -> None:
        result = run_http_exchange("/wait", client_timeout=0.02, hold_response=True)
        self.assertTrue(result.connected)
        self.assertTrue(result.timed_out)
        self.assertIsNone(result.status)

    def test_server_thread_and_listening_socket_are_cleaned_up(self) -> None:
        success = run_http_exchange("/health")
        timeout = run_http_exchange("/wait", client_timeout=0.02, hold_response=True)
        self.assertTrue(success.cleaned_up)
        self.assertTrue(timeout.cleaned_up)


if __name__ == "__main__":
    unittest.main()

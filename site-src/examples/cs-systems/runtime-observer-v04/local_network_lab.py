from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from threading import Event, Thread


HOST = "127.0.0.1"


@dataclass(frozen=True)
class HttpExchange:
    host: str
    port: int
    connected: bool
    status: int | None
    body: str
    timed_out: bool
    cleaned_up: bool


def _response(status: int, body: dict[str, str]) -> bytes:
    payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
    reason = {200: "OK", 404: "Not Found"}[status]
    headers = [
        f"HTTP/1.1 {status} {reason}",
        "Content-Type: application/json",
        f"Content-Length: {len(payload)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("ascii") + payload


def _read_request(connection: socket.socket) -> str:
    chunks = bytearray()
    while b"\r\n\r\n" not in chunks:
        chunk = connection.recv(4096)
        if not chunk:
            break
        chunks.extend(chunk)
        if len(chunks) > 16_384:
            raise ValueError("request headers too large")
    first_line = bytes(chunks).split(b"\r\n", 1)[0]
    return first_line.decode("ascii")


def _parse_response(payload: bytes) -> tuple[int, str]:
    head, body = payload.split(b"\r\n\r\n", 1)
    status_line = head.split(b"\r\n", 1)[0].decode("ascii")
    return int(status_line.split(" ", 2)[1]), body.decode("utf-8")


def run_http_exchange(
    path: str,
    *,
    client_timeout: float = 1.0,
    hold_response: bool = False,
) -> HttpExchange:
    request_received = Event()
    release_response = Event()
    server_finished = Event()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, 0))
        server.listen(1)
    except BaseException:
        server.close()
        raise
    host, port = server.getsockname()

    def serve_once() -> None:
        try:
            connection, _ = server.accept()
            with connection:
                request_line = _read_request(connection)
                request_path = request_line.split(" ", 2)[1]
                request_received.set()
                if hold_response:
                    release_response.wait(timeout=2)
                status = 200 if request_path == "/health" else 404
                body = {"status": "ok"} if status == 200 else {"error": "not_found"}
                try:
                    connection.sendall(_response(status, body))
                except OSError:
                    pass
        finally:
            server.close()
            server_finished.set()

    thread = Thread(target=serve_once, name="loopback-http-server")
    thread.start()
    connected = False
    timed_out = False
    status = None
    body = ""
    try:
        with socket.create_connection((host, port), timeout=client_timeout) as client:
            connected = True
            client.settimeout(client_timeout)
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}:{port}\r\n"
                "Connection: close\r\n\r\n"
            )
            client.sendall(request.encode("ascii"))
            request_received.wait(timeout=1)
            chunks = bytearray()
            try:
                while True:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    chunks.extend(chunk)
            except socket.timeout:
                timed_out = True
            if chunks:
                status, body = _parse_response(bytes(chunks))
    finally:
        release_response.set()
        thread.join(timeout=2)

    return HttpExchange(
        host=host,
        port=port,
        connected=connected,
        status=status,
        body=body,
        timed_out=timed_out,
        cleaned_up=server_finished.is_set() and not thread.is_alive() and server.fileno() == -1,
    )


def main() -> None:
    success = run_http_exchange("/health")
    missing = run_http_exchange("/missing")
    timeout = run_http_exchange("/wait", client_timeout=0.02, hold_response=True)

    print(f"tcp: connected={success.connected} loopback={success.host == HOST}")
    print(f"http: status={success.status} body={success.body}")
    print(f"http error: status={missing.status}")
    print(f"timeout: timed_out={timeout.timed_out} cleaned_up={timeout.cleaned_up}")


if __name__ == "__main__":
    main()

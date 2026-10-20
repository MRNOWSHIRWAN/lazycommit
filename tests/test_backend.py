import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lazycommit import backend


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        req = json.loads(body)
        assert req["model"] == "test-model"
        assert req["messages"][0]["role"] == "system"
        reply = {
            "choices": [
                {"message": {"role": "assistant", "content": "feat: add thing"}}
            ]
        }
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture()
def fake_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/v1"
    server.shutdown()


def test_chat_round_trip(fake_server):
    out = backend.chat(
        [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}],
        base_url=fake_server,
        model="test-model",
    )
    assert out == "feat: add thing"


def test_unreachable_server_raises_honest_error():
    with pytest.raises(backend.BackendError) as exc:
        backend.chat([], base_url="http://127.0.0.1:9/v1", timeout=2)
    assert "could not reach a local model server" in str(exc.value)

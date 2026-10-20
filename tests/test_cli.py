import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lazycommit import cli


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        reply = {"choices": [{"message": {"content": "feat: add greeting module"}}]}
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=tmp_path, check=True)
    (tmp_path / "greet.py").write_text("def hello():\n    return 'hi'\n")
    subprocess.run(["git", "add", "greet.py"], cwd=tmp_path, check=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def fake_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/v1"
    server.shutdown()


def test_print_only(repo, fake_server, capsys):
    rc = cli.main(["--base-url", fake_server])
    out = capsys.readouterr().out
    assert rc == 0
    assert "feat: add greeting module" in out
    # print-only mode must not commit
    log = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
    assert log.stdout == ""


def test_commit_mode(repo, fake_server, capsys):
    rc = cli.main(["--base-url", fake_server, "--commit"])
    assert rc == 0
    log = subprocess.run(
        ["git", "log", "--format=%s"], capture_output=True, text=True
    ).stdout.strip()
    assert log == "feat: add greeting module"


def test_nothing_staged(repo, fake_server, capsys):
    subprocess.run(["git", "reset", "-q"], check=True)
    rc = cli.main(["--base-url", fake_server])
    err = capsys.readouterr().err
    assert rc == 2
    assert "nothing staged" in err

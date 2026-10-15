"""An occupied local port must not trap the Windows launcher in readiness polling."""
import shutil
import socket
import subprocess
import sys
import threading

import pytest


@pytest.mark.windows_worker
@pytest.mark.parametrize('responds', [True, False], ids=['unrelated-http', 'silent-tcp'])
def test_launcher_rejects_occupied_port_without_hanging(tmp_path, repo_root, responds):
    fixture = tmp_path / 'launcher checkout with spaces'
    scripts = fixture / 'scripts'
    scripts.mkdir(parents=True)
    shutil.copyfile(repo_root / 'scripts/start_workshop.ps1', scripts / 'start_workshop.ps1')
    # Keep readiness prerequisites out of this network-boundary regression.
    # The attempted bridge exits as it would after failing to bind the port.
    (scripts / 'serve_workshop.py').write_text(
        "import sys,time\nif '--check-only' in sys.argv: raise SystemExit(0)\n"
        "time.sleep(.5)\nraise SystemExit(1)\n", encoding='utf-8')
    pwsh = shutil.which('pwsh')
    assert pwsh, 'PowerShell 7 is required for Windows launcher acceptance'
    stopping = threading.Event()
    connections = []
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        listener.settimeout(.1)
        port = listener.getsockname()[1]

        def occupy():
            while not stopping.is_set():
                try:
                    connection, _ = listener.accept()
                except socket.timeout:
                    continue
                connections.append(connection)
                if responds:
                    connection.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                                       b'Content-Length: 2\r\nConnection: close\r\n\r\n{}')
                    connection.close()

        thread = threading.Thread(target=occupy, daemon=True)
        thread.start()
        process = subprocess.Popen(
            [pwsh, '-NoProfile', '-File', str(scripts / 'start_workshop.ps1'),
             '-NoBrowser', '-Port', str(port), '-PythonPath', sys.executable],
            cwd=fixture, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            try:
                stdout, stderr = process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                pytest.fail('Launcher hung querying an unrelated occupied port')
            assert process.returncode != 0, stdout
            assert 'Workshop startup failed' in stderr, stderr
            # Failure must preserve the unrelated listener.
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                pass
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)
            stopping.set()
            thread.join(timeout=2)
            for connection in connections:
                connection.close()

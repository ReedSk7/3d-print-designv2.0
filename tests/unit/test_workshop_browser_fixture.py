"""The browser fixture must exit cleanly with its parent's stdin pipe open."""
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
import sys
from urllib.request import Request, urlopen

import pytest


@pytest.mark.parametrize("stop_method", ["http", "stdin_eof"])
def test_synthetic_fixture_exits_cleanly(repo_root, tmp_path, stop_method):
    # Only data/build preparation is omitted: use the real fixture main and
    # localhost bridge, with no browser, generated model, or owner data.
    code = (
        "import scripts._workshop_browser_fixture as fixture; "
        "fixture.prepare = lambda root: None; fixture.main()"
    )
    process = subprocess.Popen(
        [sys.executable, "-B", "-c", code, str(tmp_path)],
        cwd=repo_root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    reader = ThreadPoolExecutor(max_workers=1)
    try:
        ready = reader.submit(process.stdout.readline).result(timeout=10)
        assert ready, process.stderr.read()
        url = json.loads(ready)["url"]
        if stop_method == "http":
            with urlopen(url + "/api/session", timeout=5) as response:
                token = json.load(response)["token"]
            request = Request(
                url + "/api/stop",
                data=b"{}",
                headers={"Content-Type": "application/json", "X-Workshop-Token": token},
                method="POST",
            )
            with urlopen(request, timeout=5) as response:
                assert response.status == 200
                assert json.load(response) == {"stopping": True}
            # The browser's clean-exit check intentionally leaves this open.
            assert not process.stdin.closed
        else:
            process.stdin.close()
        result = process.wait(timeout=5)
        assert result == 0, process.stderr.read()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        reader.shutdown(wait=True, cancel_futures=True)
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()

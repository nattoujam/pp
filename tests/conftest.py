import os
import subprocess
import threading
import uuid
from pathlib import Path

import pytest

from tests.mock_server import create_server

PP_SCRIPT = Path(__file__).parent.parent / 'pp'


@pytest.fixture(scope='session')
def server_url():
    server = create_server()
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://{host}:{port}'
    server.shutdown()


@pytest.fixture
def unique_code():
    return uuid.uuid4().hex[:8]


def run_pp(*args: str, server: str, stdin: bytes | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, 'PIPING_SERVER': server}
    return subprocess.run(
        ['sh', str(PP_SCRIPT), *args],
        env=env,
        input=stdin,
        capture_output=True,
    )


def run_pp_concurrent(send_args: list[str], recv_args: list[str], server: str, send_stdin: bytes | None = None) -> tuple[subprocess.CompletedProcess, subprocess.CompletedProcess]:
    '''Run send and receive concurrently, return (send_result, recv_result).'''
    recv_result: dict[str, subprocess.CompletedProcess] = {}

    def do_recv() -> None:
        recv_result['proc'] = run_pp(*recv_args, server=server)

    thread = threading.Thread(target=do_recv)
    thread.start()

    send_result = run_pp(*send_args, server=server, stdin=send_stdin)

    thread.join(timeout=10)
    return send_result, recv_result['proc']

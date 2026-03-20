from tests.conftest import run_pp, run_pp_concurrent

# ===== send / receive =====


def test_send_receive_via_stdin(server_url, unique_code):
    data = b'hello piping'
    send, recv = run_pp_concurrent(
        send_args=['s', unique_code],
        recv_args=['r', unique_code],
        server=server_url,
        send_stdin=data,
    )
    assert send.returncode == 0
    assert recv.returncode == 0
    assert recv.stdout == data


def test_send_receive_via_file(server_url, unique_code, tmp_path):
    data = b'file content'
    src = tmp_path / 'input.txt'
    src.write_bytes(data)

    send, recv = run_pp_concurrent(
        send_args=['s', unique_code, '-f', str(src)],
        recv_args=['r', unique_code],
        server=server_url,
    )
    assert send.returncode == 0
    assert recv.returncode == 0
    assert recv.stdout == data


def test_send_receive_binary(server_url, unique_code):
    data = bytes(range(256)) * 100
    send, recv = run_pp_concurrent(
        send_args=['s', unique_code],
        recv_args=['r', unique_code],
        server=server_url,
        send_stdin=data,
    )
    assert send.returncode == 0
    assert recv.returncode == 0
    assert recv.stdout == data


# ===== error handling =====


def test_send_without_code(server_url):
    result = run_pp('s', server=server_url)
    assert result.returncode != 0


def test_receive_without_code(server_url):
    result = run_pp('r', server=server_url)
    assert result.returncode != 0


def test_send_file_not_found(server_url, unique_code):
    result = run_pp('s', unique_code, '-f',
                    '/nonexistent/file.txt', server=server_url)
    assert result.returncode != 0
    assert b'file not found' in result.stderr


def test_send_file_flag_without_path(server_url, unique_code):
    result = run_pp('s', unique_code, '-f', server=server_url)
    assert result.returncode != 0


# ===== version =====


def test_version(server_url):
    result = run_pp('--version', server=server_url)
    assert result.returncode == 0
    assert b'pp' in result.stdout

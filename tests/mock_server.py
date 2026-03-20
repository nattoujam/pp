'''
Minimal piping-server mock.

PUT /code  -> store data, signal availability
GET /code  -> wait for data, return it
'''

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


class PipingStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._events: dict[str, threading.Event] = {}
        self._data: dict[str, bytes] = {}

    def _get_or_create_event(self, code: str) -> threading.Event:
        with self._lock:
            if code not in self._events:
                self._events[code] = threading.Event()
            return self._events[code]

    def put(self, code: str, data: bytes) -> None:
        event = self._get_or_create_event(code)
        with self._lock:
            self._data[code] = data
        event.set()

    def get(self, code: str, timeout: float = 10.0) -> bytes | None:
        event = self._get_or_create_event(code)
        if not event.wait(timeout):
            return None
        with self._lock:
            data = self._data.pop(code, None)
            self._events.pop(code, None)
        return data


class PipingHandler(BaseHTTPRequestHandler):
    store: PipingStore  # set on server instance

    def do_PUT(self) -> None:
        code = self.path.lstrip('/')
        data = self._read_body()
        self.server.store.put(code, data)  # type: ignore[attr-defined]
        self.send_response(200)
        self.end_headers()

    def do_GET(self) -> None:
        code = self.path.lstrip('/')
        data = self.server.store.get(code)  # type: ignore[attr-defined]
        if data is None:
            self.send_response(504)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> bytes:
        transfer_encoding = self.headers.get('Transfer-Encoding', '')
        content_length = self.headers.get('Content-Length')

        if content_length:
            return self.rfile.read(int(content_length))

        if 'chunked' in transfer_encoding:
            chunks = []
            while True:
                line = self.rfile.readline().strip()
                chunk_size = int(line, 16)
                if chunk_size == 0:
                    break
                chunks.append(self.rfile.read(chunk_size))
                self.rfile.read(2)  # CRLF
            return b''.join(chunks)

        return self.rfile.read()


class ThreadedPipingServer(ThreadingMixIn, HTTPServer):
    store: PipingStore


def create_server(host: str = '127.0.0.1', port: int = 0) -> ThreadedPipingServer:
    server = ThreadedPipingServer((host, port), PipingHandler)
    server.store = PipingStore()
    return server

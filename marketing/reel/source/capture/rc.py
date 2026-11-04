#!/usr/bin/env python3
"""rc.py <command>...: runs server commands over RCON (the reel server: port 25575, password 'reel')."""
import socket
import struct
import sys


class Rcon:
    def __init__(self, host='127.0.0.1', port=25575, password='reel', timeout=600):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.i = 0
        self._send(3, password)

    def _send(self, kind, body):
        self.i += 1
        data = struct.pack('<ii', self.i, kind) + body.encode() + b'\x00\x00'
        self.s.sendall(struct.pack('<i', len(data)) + data)
        n = struct.unpack('<i', self._read(4))[0]
        pkt = self._read(n)
        return pkt[8:-2].decode(errors='replace')

    def _read(self, n):
        b = b''
        while len(b) < n:
            c = self.s.recv(n - len(b))
            if not c:
                raise ConnectionError('rcon closed')
            b += c
        return b

    def command(self, c):
        return self._send(2, c.lstrip('/'))


if __name__ == '__main__':
    r = Rcon()
    for c in sys.argv[1:]:
        out = r.command(c)
        if out.strip():
            print(out)

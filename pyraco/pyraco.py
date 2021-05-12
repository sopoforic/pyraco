"""Main module."""
import logging
import re
import socket
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Status:
    status: str
    system: str
    game: str
    crc32: str


class InvalidResponseError(RuntimeError):
    pass


class Connection:
    def __init__(self, addr="localhost", port=55355, debug=False):
        self._addr = addr
        self._port = port

        if debug:
            try:
                version = self.version()
                if version:
                    logger.debug("Connected to retroarch v%s.", version)
            except socket.timeout:
                logger.exception("Timeout: could not get version from retroarch.")

    def _send(self, msg, timeout=1, recv_buffer=4096):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.connect((self._addr, self._port))
            s.sendall(msg.encode('ascii') + b'\n')
            return s.recv(recv_buffer).decode().strip()

    def version(self):
        return self._send('VERSION', recv_buffer=16)

    def get_status(self):
        r = self._send('GET_STATUS')

        if r == 'GET_STATUS CONTENTLESS':
            return Status('CONTENTLESS', None, None, None)

        m = re.search(r'GET_STATUS ([^ ]+) (.+?),(.+?),crc32=([0-9a-f]+)', r)
        if not m:
            raise InvalidResponseError(r)

        return Status(m.group(1), m.group(2), m.group(3), m.group(4))

    def read_core_ram(self, addr, length):
        r = self._send('READ_CORE_RAM {:x} {:d}'.format(addr, length), recv_buffer=16384)
        if not r.startswith('READ_CORE_RAM'):
            raise InvalidResponseError(r)

        data = r.split(maxsplit=2)[2]
        if data == '-1':
            return None

        return bytes.fromhex(data)

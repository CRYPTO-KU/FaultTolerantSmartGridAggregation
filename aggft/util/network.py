import json
import re
import selectors
import socket

from uuid import uuid4

import log

from dataclasses import dataclass
from typing import Callable, Tuple
from uuid import UUID

# TODO: Remove
from time import time as now
# from .time import Time


# Types

Host = str
Port = int
Address = Tuple[Host, Port]

@dataclass
class _LISTENING_SOCKET:
    id: UUID

@dataclass
class _CONNECTION_SOCKET:
    id: UUID
    address: Address
    data: str = ""

# Constants

LOCALHOST = "localhost"

# def listen_to_json_once(port: PORT, timeout: float, start_marker: str, end_marker: str) -> Tuple[bool, dict]:
#     ok, data = listen_once(port, timeout, start_marker, end_marker)
#     if not ok:
#         return (False, {})
#     try:
#         json_data = json.loads(data)
#         return (True, json_data)
#     except json.JSONDecodeError:
#         return (False, {})

def listen_multiple(
    port: Port, stop_no_later_than: float, # TODO: Use Time
    start_marker: str, end_marker: str,
    validator: Callable[[str], bool] = lambda _ : True,
    early_stoper: Callable[[Tuple[str, ...]], bool] = lambda _ : False
):
    selector = selectors.DefaultSelector()

    listening_id = uuid4()
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind((LOCALHOST, port))
    listening_socket.listen()
    listening_socket.setblocking(False)
    selector.register(
        listening_socket,
        selectors.EVENT_READ,
        data = _LISTENING_SOCKET(listening_id)
    )
    log.info(f"[{listening_id}] Listening on port: {port}.")

    while True:
        if now() > stop_no_later_than:
            break
        # Setting timeout to zero makes it non-blocking
        events = selector.select(timeout = 0)
        for key, mask in events:
            if isinstance(key.data, _LISTENING_SOCKET):
                accept_connection(key.fileobj, key.data.id, selector)
            elif isinstance(key.data, _CONNECTION_SOCKET):
                pass
                # service_connection(key, mask)

    log.info(f"[{listening_id}] Stop listining on port: {port}.")
    selector.close()

def accept_connection(socket: socket.socket, listening_id: UUID, selector: selectors.DefaultSelector):
    # Socket should be ready to read immediately
    connection, address = socket.accept()
    connection.setblocking(False)
    connection_id = uuid4()
    selector.register(
        connection,
        selectors.EVENT_READ | selectors.EVENT_WRITE,
        data = _CONNECTION_SOCKET(connection_id, address)
    )
    log.info(f"[{listening_id}] Accepted connection [{connection_id}] from: {address}.")

# def handle_connection(key, mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         if recv_data:
#             data.outb += recv_data
#         else:
#             print(f"Closing connection to {data.addr}")
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if data.outb:
#             print(f"Echoing {data.outb!r} to {data.addr}")
#             sent = sock.send(data.outb)  # Should be ready to write
#             data.outb = data.outb[sent:]

# def listen_once(port: PORT, timeout: float, start_marker: str, end_marker: str) -> Tuple[bool, str]:
#     print(f"Started at {now()}")
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind(("localhost", port))
#         s.listen()
#         s.settimeout(timeout)
#         try:
#             connection, _ = s.accept()
#             connection.settimeout(timeout)
#             print(f"Connected at {now()}")
#             with connection:
#                 data = receive_all(connection, start_marker, end_marker)
#                 connection.sendall(str.encode(f"{start_marker}ACK{end_marker}"))
#                 return (True, data)
#                 
#         except socket.timeout:
#             print(f"Timed out at {now()}")
#             return (False, "")
#
# def receive_all(connection: socket.socket, start_marker: str, end_marker: str) -> str:
#     MB = 8192
#     data = ""
#     while True:
#         chunk = connection.recv(MB)
#         print(f"Received chunk at {now()}")
#         data = f"{data}{chunk}"
#         match = re.search(f"{start_marker}(?P<msg>.*){end_marker}", data)
#         if match is not None:
#             return match.group("msg")

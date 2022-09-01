# Standard Library Imports

import re
import selectors
import socket

from time import time as now
from uuid import uuid4

# Project Imports

from . import log

# Standard Library Type Imports

from dataclasses import dataclass
from typing import Callable, Tuple
from uuid import UUID
from enum import Enum

# Project Type Imports

from .time import Time

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

class _STATE(Enum):
    IN_PROGRESS = 0
    SUCCESS = 1
    FAILED = 2

# Constants

LOCALHOST = "localhost"
MEGA_BYTE = 8192

def listen_multiple(
    port: Port, stop_no_later_than: Time,
    start_marker: str, end_marker: str,
    early_stopper: Callable[[Tuple[str, ...]], bool] = lambda _: False
) -> Tuple[str, ...]:
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

    results = ()

    while True:
        if now() > stop_no_later_than: break
        # Setting timeout to zero makes it non-blocking
        events = selector.select(timeout = 0)
        should_early_stop = False
        for key, masks in events:
            if now() > stop_no_later_than: break
            elif isinstance(key.data, _LISTENING_SOCKET):
                accept_connection(key, selector)
            elif isinstance(key.data, _CONNECTION_SOCKET):
                state = handle_connection(key, masks, selector, start_marker, end_marker)
                if state == _STATE.SUCCESS:
                    results = (*results, key.data.data)
                    should_early_stop = early_stopper(results)
                    if should_early_stop:
                        log.info(f"[{listening_id}] Early stopping...")
                        break
        if should_early_stop: break

    log.info(f"[{listening_id}] Stop listining on port: {port}.")
    selector.close()
    return results

def accept_connection(key: selectors.SelectorKey, selector: selectors.DefaultSelector):
    socket = key.fileobj
    listening_id = key.data.id
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

def handle_connection(key: selectors.SelectorKey, masks: int, selector: selectors.DefaultSelector, start_marker: str, end_marker: str) -> _STATE:
    masks_include = lambda masks, event: masks & event
    socket = key.fileobj
    socket_data = key.data
    if masks_include(masks, selectors.EVENT_READ):
        # Socket should be ready to read immediately
        chunk = socket.recv(MEGA_BYTE)
        socket_data.data = f"{socket_data.data}{chunk}"

        match = re.search(f"{start_marker}(?P<msg>.*){end_marker}", socket_data.data)

        if not chunk:
            log.info(f"[{socket_data.id}] No chunk received. Aborting connection to {socket_data.address}...")
            selector.unregister(socket)
            socket.close()
            return _STATE.FAILED

        if match is not None:
            socket_data.data = match.group("msg")
            log.info(f"[{socket_data.id}] Received all data. Closing connection to {socket_data.address}...")
            if masks_include(masks, selectors.EVENT_WRITE):
                # Socket should be ready to write immediately
                socket.sendall(str.encode(f"{start_marker}ACK{end_marker}"))
            selector.unregister(socket)
            socket.close()
            return _STATE.SUCCESS
        
        log.info(f"[{socket_data.id}] Received chunk.")

    return _STATE.IN_PROGRESS

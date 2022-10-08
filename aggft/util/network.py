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
from typing import Any, Callable, Tuple
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
    send: bytes = b""
    recv: str = ""

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
    listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
                state = handle_read_connection(key, masks, selector, start_marker, end_marker)
                if state == _STATE.SUCCESS:
                    results = (*results, key.data.recv)
                    should_early_stop = early_stopper(results)
                    if should_early_stop:
                        log.info(f"[{listening_id}] Early stopping...")
                        break
        if should_early_stop:
            log.info(f"[{listening_id}] Early stopping...")
            break

    log.info(f"[{listening_id}] Stop listining on port: {port}.")
    selector.close()
    return results

def accept_connection(key: Any, selector: selectors.DefaultSelector):
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

def handle_read_connection(key: Any, masks: int, selector: selectors.DefaultSelector, start_marker: str, end_marker: str) -> _STATE:
    masks_include = lambda masks, event: masks & event
    socket = key.fileobj
    socket_data = key.data
    if masks_include(masks, selectors.EVENT_READ):
        # Socket should be ready to read immediately
        chunk = socket.recv(MEGA_BYTE)
        socket_data.recv = f"{socket_data.recv}{chunk}"

        match = re.search(f"{start_marker}(?P<msg>.*){end_marker}", socket_data.recv)

        if not chunk:
            log.info(f"[{socket_data.id}] No chunk received. Aborting connection to {socket_data.address}...")
            selector.unregister(socket)
            socket.close()
            return _STATE.FAILED

        if match is not None:
            socket_data.recv = match.group("msg")
            log.info(f"[{socket_data.id}] Received all data. Closing connection to {socket_data.address}...")
            if masks_include(masks, selectors.EVENT_WRITE):
                # Socket should be ready to write immediately
                socket.sendall(str.encode(f"{start_marker}ACK{end_marker}"))
            selector.unregister(socket)
            socket.close()
            return _STATE.SUCCESS
        
        log.info(f"[{socket_data.id}] Received chunk.")

    return _STATE.IN_PROGRESS

def send(
    address: Address, content: str, stop_no_later_than: Time,
    start_marker: str, end_marker: str
) -> bool:
    selector = selectors.DefaultSelector()

    connection_id = uuid4()
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_socket.setblocking(False)
    connection_socket.connect_ex(address)
    selector.register(
        connection_socket,
        selectors.EVENT_READ | selectors.EVENT_WRITE,
        data = _CONNECTION_SOCKET(connection_id, address, str.encode(f"{start_marker}{content}{end_marker}"))
    )
    log.info(f"[{connection_id}] Starting connection to address: {address}.")

    result = False
    done = False

    while True:
        if done or now() > stop_no_later_than: break
        # Setting timeout to zero makes it non-blocking
        events = selector.select(timeout = 0)
        for key, masks in events:
            if now() > stop_no_later_than: break
            elif isinstance(key.data, _CONNECTION_SOCKET):
                state = handle_write_connection(key, masks, selector, start_marker, end_marker)
                if state == _STATE.SUCCESS:
                    result = True
                    done = True
                elif state == _STATE.FAILED:
                    result = False
                    done = True

    log.info(f"[{connection_id}] Stopped connection to address: {address}.")
    selector.close()
    return result

def handle_write_connection(key: Any, masks: int, selector: selectors.DefaultSelector, start_marker: str, end_marker: str) -> _STATE:
    masks_include = lambda masks, event: masks & event
    socket = key.fileobj
    socket_data = key.data
    if socket_data.send and masks_include(masks, selectors.EVENT_WRITE):
        # Socket should be ready to write immediately
        try:
            sent = socket.send(socket_data.send)
        except ConnectionRefusedError:
            selector.unregister(socket)
            socket.close()
            return _STATE.FAILED

        socket_data.send = socket_data.send[sent:]
    elif masks_include(masks, selectors.EVENT_READ):
        # Socket should be ready to read immediately
        chunk = socket.recv(MEGA_BYTE)
        socket_data.recv = f"{socket_data.recv}{chunk}"

        match = re.search(f"{start_marker}(?P<msg>.*){end_marker}", socket_data.recv)

        if not chunk:
            log.info(f"[{socket_data.id}] No chunk received. Aborting connection to {socket_data.address}...")
            selector.unregister(socket)
            socket.close()
            return _STATE.FAILED

        if match is not None:
            socket_data.recv = match.group("msg")
            log.info(f"[{socket_data.id}] Received all data. Closing connection to {socket_data.address}...")
            selector.unregister(socket)
            socket.close()
            return _STATE.SUCCESS if socket_data.recv == "ACK" else _STATE.FAILED
        
        log.info(f"[{socket_data.id}] Received chunk.")

    return _STATE.IN_PROGRESS

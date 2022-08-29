import json
import re
import socket

from typing import Tuple

ADDRESS = Tuple[str, int]

def listen_to_json_once(address: ADDRESS, timeout: float, start_marker: str, end_marker: str) -> Tuple[bool, dict]:
    ok, data = listen_once(address, timeout, start_marker, end_marker)
    if not ok:
        return (False, {})
    try:
        json_data = json.loads(data)
        return (True, json_data)
    except json.JSONDecodeError:
        return (False, {})

def listen_once(address: ADDRESS, timeout: float, start_marker: str, end_marker: str) -> Tuple[bool, str]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(address)
        s.listen()
        s.settimeout(timeout)
        try:
            connection, _ = s.accept()
            with connection:
                data = receive_all(connection, start_marker, end_marker)
                connection.sendall(str.encode(f"{start_marker}ACK{end_marker}"))
                return (True, data)
                
        except socket.timeout:
            return (False, "")

def receive_all(connection: socket.socket, start_marker: str, end_marker: str) -> str:
    MB = 8192
    data = ""
    while True:
        chunk = connection.recv(MB)
        data = f"{data}{chunk}"
        match = re.search(f"{start_marker}(?P<msg>.*){end_marker}", data)
        if match is not None:
            return match.group("msg")

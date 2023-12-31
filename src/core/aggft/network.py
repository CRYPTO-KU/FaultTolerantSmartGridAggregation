import asyncio
import json
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from typing import Any, Dict, Tuple

import aiohttp
from aiohttp import web

################################################################################
# Types
################################################################################

Host = str
Port = int
Registry = Dict[Tuple[Host, Port], Queue]


@dataclass(frozen=True)
class Address:
    host: Host
    port: Port
    valid: bool


################################################################################
# Abstract Network Manager
################################################################################

# AggFT can work with any networking protocol.
# Implement the NetworkManager abstract class for new network protocols.


class NetworkManager(ABC):
    @abstractmethod
    def send(self, address: Address, data: Dict[str, Any], timeout: float) -> bool:
        pass

    @abstractmethod
    def listen(self, address: Address) -> Queue:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


################################################################################
# Shared Memory Networking
################################################################################


# Uses shared memory instead of sending actual network requests.
# Can be used for simulations on one physical machine.


class SharedMemoryNetworkManager(NetworkManager):
    def __init__(self, id, registry: Registry, link_status, sm_status):
        self.id = id
        self.registry = registry
        self.dummy_queue = Queue()
        self.link_status = link_status
        self.sm_status = sm_status

    def send(self, address: Address, data: Dict[str, Any], _) -> bool:
        if self.link_status[(self.id, address.port)] and (
            address.port == -1 or self.sm_status[address.port]
        ):
            self.registry[(address.host, address.port)].put(
                json.loads(json.dumps(data))
            )
            return True
        # Use dummy queue to make successful and failed send operation take
        # similar time
        self.dummy_queue.put(json.loads(json.dumps(data)))
        self.dummy_queue.get()
        return False

    def listen(self, address: Address) -> Queue:
        return self.registry[(address.host, address.port)]

    def stop(self) -> None:
        pass


################################################################################
# HTTP Networking
################################################################################


# Uses the HTTP network protocol.
# Can be used for simulations on one physical machine or multiple.


class HTTPNetworkManager(NetworkManager):
    def __init__(self):
        self.port = 8000
        self.queue = Queue()
        self.thread = threading.Thread(target=asyncio.run, args=(self._run(),))
        self.running = True

    async def _run(self):
        async def handler(request):
            data = await request.json()
            self.queue.put(data)
            return web.Response(text="OK")

        app = web.Application()
        app.add_routes([web.post("/", handler)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port, reuse_port=True)
        await site.start()

        while self.running:
            await asyncio.sleep(1)

        await runner.cleanup()

    def send(self, address: Address, data: Dict[str, Any], timeout: float) -> bool:
        if not address.valid:
            return False
        return asyncio.run(self._send(address, data, timeout))

    def listen(self, address: Address) -> Queue:
        self.port = address.port
        self.thread.start()
        return self.queue

    def stop(self) -> None:
        self.running = False

    async def _send(self, address: Address, data: Dict[str, Any], timeout: float):
        client_timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            url = f"http://{address.host}:{address.port}"
            try:
                async with session.post(url, json=data) as resp:
                    return resp.status == 200
            except:
                return False

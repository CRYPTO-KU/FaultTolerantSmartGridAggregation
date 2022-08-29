from aggft.dc.masking import MaskingDC
from typing import Any, Dict, List, Tuple
from aggft.util.timeoutable_coroutine import TimeoutableCoroutine
from aggft.types.url import URL
from sortedcontainers import SortedSet
from aiohttp import web
import aiohttp
import asyncio

class HTTPMaskingDCPhase1Server(TimeoutableCoroutine[Tuple[SortedSet, Dict[int, Any]]]):
    def __init__(self):
        self.data = asyncio.Queue()
        self.runner: web.AppRunner

    async def _coroutine(self, round: int, n_min: int, port: int) -> Tuple[SortedSet, Dict[int, Any]]:
        async def handler(request: web.Request) -> web.Response:
            # Insure the request has a readable body
            if not (request.body_exists and request.can_read_body):
                raise web.HTTPBadRequest
            # Extract request data
            try:
                body = await request.json()
            except:
                raise web.HTTPBadRequest
            # Insure request contains all required fields
            if not all(map(lambda k : k in body, ["round", "smartMeterID", "maskedMeasurement"])):
                raise web.HTTPBadRequest
            # Insure request is for the correct round
            if body["round"] != round:
                raise web.HTTPBadRequest

            smart_meter_id = body["smartMeterID"]
            masked_measurement = body["maskedMeasurement"]

            # Save data
            await self.data.put((smart_meter_id, masked_measurement))

            # Respond to sender with ACK
            return web.json_response({
                "msg": "ACK"
            })

        app = web.Application()
        app.add_routes([web.post("/phase-1", handler)])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "localhost", port)
        await site.start()

        while True:
            await asyncio.sleep(1000)

    async def _on_timeout(self) -> Tuple[SortedSet, Dict[int, Any]]:
        return await self.return_result()

    async def return_result(self) -> Tuple[SortedSet, Dict[int, Any]]:
        await self.runner.cleanup()
        l_rem = SortedSet()
        data = {}
        while not self.data.empty():
            smart_meter_id, masked_measurement = await self.data.get()
            l_rem.add(smart_meter_id)
            data[smart_meter_id] = masked_measurement
        return (l_rem, data)

class HTTPMaskingDCPhase2Server(TimeoutableCoroutine[Tuple[SortedSet, int]]):
    def __init__(self):
        self.l_act: SortedSet
        self.s_final: int
        self.runner: web.AppRunner

    async def _coroutine(self, round: int, port: int) -> Tuple[SortedSet, int]:
        async def handler(request: web.Request) -> web.Response:
            # Only accept one request in the second phase
            if self.l_act:
                raise web.HTTPBadRequest
            # Insure the request has a readable body
            if not (request.body_exists and request.can_read_body):
                raise web.HTTPBadRequest
            # Extract request data
            try:
                body = await request.json()
            except:
                raise web.HTTPBadRequest
            # Insure request contains all required fields
            if not all(map(lambda k : k in body, ["round", "listActivated", "sFinal"])):
                raise web.HTTPBadRequest
            # Insure request is for the correct round
            if body["round"] != round:
                raise web.HTTPBadRequest

            self.l_act = SortedSet(body["listActivated"])
            self.s_final = body["sFinal"]

            # Respond to sender with ACK
            return web.json_response({
                "msg": "ACK"
            })

        app = web.Application()
        app.add_routes([web.post("/phase-2", handler)])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "localhost", port)
        await site.start()

        while True:
            await asyncio.sleep(1000)
            if self.l_act:
                return await self.return_result()

    async def _on_timeout(self) -> Tuple[SortedSet, int]:
        return await self.return_result()

    async def return_result(self) -> Tuple[SortedSet, int]:
        await self.runner.cleanup()
        return (self.l_act, self.s_final)

class HTTPMaskingDC(MaskingDC):
    def _get_phase_1_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, Dict[int, Any]]]:
        return HTTPMaskingDCPhase1Server()

    def _get_phase_2_server(self) -> TimeoutableCoroutine[Tuple[SortedSet, int]]:
        return HTTPMaskingDCPhase2Server()

    async def _activate_smart_meter(self, l_rem: SortedSet, s_init: int) -> None:
        data = { "listRemaining": l_rem, "sInitial": s_init }
        for address in l_rem:
            address = self.sm_addresses[l_rem[0]]
            async with aiohttp.ClientSession() as session:
                async with session.post(address, json = data) as response:
                    if response.status == 200:
                        return

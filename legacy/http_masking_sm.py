import secrets
from aggft.masking_sm import MaskingSM
from typing import Any, Dict, List, Tuple
from aggft.util.timeoutable_coroutine import TimeoutableCoroutine
from aggft.types.url import URL
from sortedcontainers import SortedSet
from aiohttp import web
import aiohttp
import asyncio

class HTTPMaskingSMServer(TimeoutableCoroutine[Tuple[bool, SortedSet, SortedSet, int]]):
    def __init__(self):
        self.l_rem: SortedSet
        self.l_act: SortedSet
        self.s: int
        self.runner: web.AppRunner

    async def _coroutine(self, round: int, url: URL) -> Tuple[bool, SortedSet, SortedSet, int]:
        async def handler(request: web.Request) -> web.Response:
            # Only accept one request in the final activation
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
            if not all(map(lambda k : k in body, ["round", "listRemaining", "listActivated", "s"])):
                raise web.HTTPBadRequest
            # Insure request is for the correct round
            if body["round"] != round:
                raise web.HTTPBadRequest

            self.l_rem = SortedSet(body["listRemaining"])
            self.l_act = SortedSet(body["listActivated"])
            self.s = body["s"]

            # Respond to sender with ACK
            return web.json_response({
                "msg": "ACK"
            })

        app = web.Application()
        app.add_routes([web.post("/activate", handler)])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "localhost", url.port)
        await site.start()

        while True:
            await asyncio.sleep(1000)
            if self.l_act:
                return await self.return_result(True)

    async def _on_timeout(self) -> Tuple[bool, SortedSet, SortedSet, int]:
        return await self.return_result(False)

    async def return_result(self, ok) -> Tuple[bool, SortedSet, SortedSet, int]:
        await self.runner.cleanup()
        return (ok, self.l_rem, self.l_act, self.s)

class HTTPMaskingSM(MaskingSM):
    def _get_server(self) -> TimeoutableCoroutine[Tuple[bool, SortedSet, SortedSet, int]]:
        return HTTPMaskingSMServer()

    async def _send_msg(self, to: str, data: Dict[str, Any]) -> bool:
        print(to, data)
        async with aiohttp.ClientSession() as session:
            print("yo")
            async with session.post(to, json = data) as response:
                print("yo")
                print("yo")
                return response.status == 200

    def _get_initial_msg(self, round: int, data: Any, si: int) -> Dict[str, Any]:
        return {
            "round": round,
            "smartMeterID": self.id,
            "maskedMeasurement": data
        }

    def _get_middle_msg(self, round: int, l_rem: SortedSet, l_act: SortedSet, s_current: int) -> Dict[str, Any]:
        return {
            "round": round,
            "listRemaining": l_rem,
            "listActivated": l_act,
            "s": s_current
        }

    def _get_final_msg(self, round: int, l_act: SortedSet, s: int) -> Dict[str, Any]:
        return {
            "round": round,
            "listActivated": l_act,
            "sFinal": s
        }

class TestHTTPMaskingSM(HTTPMaskingSM):
    async def run(self) -> None:
        print(f"TestHTTPMaskingSM {self.id}: run()")
        return await super().run()

    def _get_data(self, round: int) -> Any:
        data =  secrets.randbelow(self.k)
        print(f"Data for SM {self.id}: {data}")
        return data

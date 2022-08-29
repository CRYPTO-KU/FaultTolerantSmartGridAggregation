from ..util import log
from ..util import network
from ..util import time

from ..model.round import RoundMetadata

from dataclasses import dataclass, field
from time import time as now
from typing import Literal, Tuple, Dict, Callable, Any
from uuid import uuid4 as random_id
from rich.markup import escape

from aiohttp import web

import asyncio

async def run_single_round(round: int, port: int, sm_addresses: Tuple[network.ADDRESS, ...], meta: RoundMetadata, k: int):
    # Wait for the right time to start round
    round_start = meta.start + meta.round_len * round
    await asyncio.sleep(time.remaining_until(round_start))

    network.listen_to_json_once


async def run_forever(port: int, sm_addresses: Tuple[network.ADDRESS, ...], meta: RoundMetadata, k: int):
    # Wait for the right time to start operation
    await asyncio.sleep(time.remaining_until(meta.start))
    await run_single_round(0, port, sm_addresses, meta, k)

# @dataclass
# class Store:
#     round: int = -1
#     data: Dict[int, int] = field(default_factory = dict)
#
# Phase = Literal[1, 2]
# Field = Tuple[str, str, Callable[[Any], bool]]
#
# def run(port: int, sm_addresses: Tuple[str, ...], n_min: int, time: Time, k: int):
#     app = web.Application(middlewares = [ middleware.enforce_json_request ])
#     routes = web.RouteTableDef()
#
#     store = Store()
#
#     @routes.post("/phase-1")
#     async def phase_1(body):
#         id = random_id()
#         log_prefix = escape(f"[{id}] [phase-1]")
#         received_at = now()
#         log.info(f"{log_prefix} Request received.")
#         phase_1_fields = (
#             ("id", "Smart meter ID", lambda x : x in range(len(sm_addresses))),
#             ("data", "Data", lambda x : isinstance(x, int))
#         )
#         validate(body, 1, received_at, time, phase_1_fields, log_prefix)
#         log.info(f"{log_prefix} Request validated.")
#         round = current_round(received_at, time)
#         id = body["id"]
#         data = body["data"]
#
#         # Clear any data from a previous round
#         if store.round != round:
#             store.round = round
#             store.data = {}
#
#         store.data[id] = data
#
#         log.info(f"{log_prefix} Smart meter {id} sent initial data {data}.")
#
#         if len(store.data.keys()) >= n_min:
#             pass
#
#         return web.Response(text = f"ACK")
#
#     @routes.post("/phase-2")
#     async def phase_2(body):
#         id = random_id()
#         log_prefix = escape(f"[{id}] [phase-1]")
#         received_at = now()
#         log.info(f"{log_prefix} Request received.")
#         phase_1_fields = (
#             ("id", "Smart meter ID", lambda x : x in range(len(sm_addresses))),
#             ("data", "Data", lambda x : isinstance(x, int))
#         )
#         validate(body, 1, received_at, time, phase_1_fields, log_prefix)
#         log.info(f"{log_prefix} Request validated.")
#         round = current_round(received_at, time)
#         id = body["id"]
#         data = body["data"]
#
#         # Clear any data from a previous round
#         if store.round != round:
#             store.round = round
#             store.data = {}
#
#         store.data[id] = data
#
#         log.info(f"{log_prefix} Smart meter {id} sent initial data {data}.")
#
#         return web.Response(text = f"ACK")
#
#     app.add_routes(routes)
#     web.run_app(app, port = port)
#
# def validate(body: Dict, phase: Phase, received_at: float, time: Time, fields: Tuple[Field, ...], log_prefix: str):
#     validate_round(body, received_at, time, log_prefix)
#     validate_phase(phase, received_at, time, log_prefix)
#     validate_fields(body, fields, log_prefix)
#
# def validate_round(body: Dict, received_at: float, time: Time, log_prefix: str):
#     round = current_round(received_at, time)
#
#     if "round" not in body:
#         log.warning(f"{log_prefix} Round unspecified.")
#         raise web.HTTPBadRequest
#
#     if round < 0:
#         log.warning(f"{log_prefix} Operation did not start yet.")
#         raise web.HTTPBadRequest
#
#     if body["round"] != round:
#         log.warning(f"{log_prefix} Wrong round.")
#         raise web.HTTPBadRequest
#
# def validate_phase(phase: Phase, received_at: float, time: Time, log_prefix: str):
#     if phase != current_phase(received_at, time):
#         log.warning(f"{log_prefix} Wrong phase.")
#         raise web.HTTPBadRequest
#
# def validate_fields(body: Dict, fields: Tuple[Field, ...], log_prefix: str):
#     for key, name, verify in fields:
#         if key not in body:
#             log.warning(f"{log_prefix} {name} unspecified.")
#             raise web.HTTPBadRequest
#         if not verify(body[key]):
#             log.warning(f"{log_prefix} {name} invalid.")
#             raise web.HTTPBadRequest
#
# def current_round(received_at: float, time: Time) -> int:
#     return max(int((received_at - time.start) / time.round_len), -1)
#
# def current_phase(received_at: float, time: Time) -> Phase:
#     round = current_round(received_at, time)
#     boundary = time.start + time.round_len * round + time.phase_1_len
#     return 1 if received_at < boundary else 2
#     
# run(9999, ("", ""), 1, Time(now(), 20, 10, 10), 0)

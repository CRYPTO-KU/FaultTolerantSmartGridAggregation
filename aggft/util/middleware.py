from . import log

from aiohttp import web

@web.middleware
async def enforce_json_request(request, handler):
    # Insure the request has a readable body
    if not (request.body_exists and request.can_read_body):
        log.warning("Bad Request - Request does not have a readable body.")
        raise web.HTTPBadRequest
    # Extract request data
    try:
        body = await request.json()
    except:
        log.warning("Bad Request - Request body is not valid JSON.")
        raise web.HTTPBadRequest
    response = await handler(body)
    return response

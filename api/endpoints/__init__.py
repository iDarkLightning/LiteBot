from aiohttp import web
from .members import get_members

def add_routes(app, client):
    app.add_routes([
        web.get("/members", lambda request: get_members(request, client))
    ])

from aiohttp import web
from .members import get_members
from .game_message import send_game_message

def add_routes(app, client):
    app.add_routes([
        web.get("/members", lambda request: get_members(request, client)),
        web.post("/game_message", lambda request: send_game_message(request, client))
    ])

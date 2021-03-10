from .server_route import blueprint as server_blueprint
from sanic import Blueprint

ROUTES = Blueprint.group(server_blueprint)
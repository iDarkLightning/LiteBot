from .server_route import blueprint as server_blueprint
from .members_route import blueprint as member_blueprint
from sanic import Blueprint

ROUTES = Blueprint.group(server_blueprint, member_blueprint)
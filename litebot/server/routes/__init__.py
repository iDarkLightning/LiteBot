from .server_route import blueprint as server_blueprint
from .archive_route import blueprint as archive_blueprint
from sanic import Blueprint

ROUTES = Blueprint.group(server_blueprint, archive_blueprint)
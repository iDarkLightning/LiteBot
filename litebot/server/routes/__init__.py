from .server_route import blueprint as server_blueprint
from .backup_route import blueprint as backup_blueprint
from sanic import Blueprint

ROUTES = Blueprint.group(server_blueprint, backup_blueprint)
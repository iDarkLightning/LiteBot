import abc

from litebot.errors import InvalidEvent


class Payload(abc.ABC):
    EVENT_NAME = str()

    def __init__(self, ctx, args):
        pass

    @classmethod
    def get_event_payload(cls, name):
        try:
            return list(filter(lambda c: c.EVENT_NAME == name, cls.__subclasses__()))[0]
        except IndexError:
            raise InvalidEvent("Could not find a matching payload for this event!")

class ServerStartPayload(Payload):
    EVENT_NAME = "on_server_start"

class ServerStopPayload(Payload):
    EVENT_NAME = "on_server_stop"

class TickPayload(Payload):
    EVENT_NAME = "on_tick"

class PlayerJoinPayload(Payload):
    EVENT_NAME = "on_player_join"

class PlayerLeavePayload(Payload):
    EVENT_NAME = "on_player_leave"

class PlayerDeathPayload(Payload):
    EVENT_NAME = "on_player_death"

class PlayerBreaksBlockPayload(Payload):
    EVENT_NAME = "on_player_breaks_block"

    def __init__(self, ctx, args):
        super().__init__(ctx, args)
        self.block = args["block"]

class MessagePayload(Payload):
    EVENT_NAME = "on_message"

    def __init__(self, ctx, args):
        super().__init__(ctx, args)
        self.message = args["message"]



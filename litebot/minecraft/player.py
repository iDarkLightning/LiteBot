
class Player:
    def __init__(self, **data):
        self.uuid: str = data.get("uuid")
        self.pos_x: int = data.get("pos_x")
        self.pos_y: int = data.get("pos_y")
        self.pos_z: int = data.get("pos_z")
        self.dimension = data.get("dimension")
        self.op_level = data.get("op_level")

    def __repr__(self):
        return f"player=<{self.uuid}> at x={self.pos_x} y={self.pos_y} z={self.pos_z}"

    def __contains__(self, item):
        return self.uuid in item
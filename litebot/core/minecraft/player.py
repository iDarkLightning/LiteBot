class Player:
    def __init__(self, **data):
        """An object to model the player data sent from the server.

        Args:
            **data: The data to construct the class with
        """

        self.name: str = data.get("name")
        self.uuid: str = data.get("uuid")
        self.id = self.uuid
        self.pos_x: int = data.get("pos_x")
        self.pos_y: int = data.get("pos_y")
        self.pos_z: int = data.get("pos_z")
        self.dimension: str = data.get("dimension")
        self.op_level: int = data.get("op_level")

    def get_block_pos(self):
        """
        Returns:
            A tuple containing the player's block position
        """
        return self.pos_x, self.pos_y, self.pos_z

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"player=<{self.uuid}> at x={self.pos_x} y={self.pos_y} z={self.pos_z}"

    def __contains__(self, item):
        return self.uuid in item
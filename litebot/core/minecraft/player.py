from dataclasses import dataclass

@dataclass(repr=False, frozen=True)
class Player:
    """
    An object to model the player data sent from the server.
    """

    name: str
    uuid: str
    pos_x: int
    pos_y: int
    pos_z: int
    dimension: str
    op_level: int

    @property
    def block_pos(self):
        """
        Returns:
            A tuple containing the player's block position
        """
        return self.pos_x, self.pos_y, self.pos_z

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"player=<{self.uuid}> at x={self.pos_x} y={self.pos_y} z={self.pos_z}"

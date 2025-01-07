from pokemon_battle import Battle
from print_visualizer import print_visualize as visualize

from typing import Callable, Any

def battle_control(battle:Battle) -> None:
    """Controls the flow and inputs to a battle

    :param battle: The battle to control
    :type battle: Battle
    :param visualizer: A function that ouputs information so the battle is visible to the user
    :type visualizer: Callable[[str,Any],None]
    """
    pass

class BattleController:

    def __init__(self):
        pass

    def setup_cards(self):
        pass

    def turn(self):
        pass

class CommandLineBattleController(BattleController):

    def __init__(self):
        super().__init__()

    def setup_cards(self):
        return super().setup_cards()
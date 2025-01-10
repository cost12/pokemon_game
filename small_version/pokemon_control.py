from pokemon_battle import Battle, OwnDeckView, OpponentDeckView, get_opponent_deck_view, get_own_deck_view
from print_visualizer import print_visualize as visualize

from typing import Callable, Any

def battle_control(battle:Battle) -> None:
    """Controls the flow and inputs to a battle

    :param battle: The battle to control
    :type battle: Battle
    :param visualizer: A function that ouputs information so the battle is visible to the user
    :type visualizer: Callable[[str,Any],None]
    """
    battle.controller1.setup_cards(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    battle.controller2.setup_cards(get_own_deck_view(battle.deck2), get_opponent_deck_view(battle.deck1))

class BattleController:

    def __init__(self):
        pass

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> str:
        pass

    def turn(self):
        pass

class CommandLineBattleController(BattleController):

    def __init__(self):
        super().__init__()

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> str:
        pass
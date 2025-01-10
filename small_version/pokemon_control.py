from pokemon_battle import Battle, OwnDeckView, OpponentDeckView, get_opponent_deck_view, get_own_deck_view
from print_visualizer import visualize_own_deck, visualize_opponent_deck

def battle_control(battle:Battle, controller1:'BattleController', controller2:'BattleController') -> None:
    """Controls the flow and inputs to a battle

    :param battle: The battle to control
    :type battle: Battle
    
    """
    print("The battle has begun")
    print("Team 1 set up your cards")
    move1 = controller1.setup_cards(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    print("Team 2 set up your cards")
    move2 = controller2.setup_cards(get_own_deck_view(battle.deck2), get_opponent_deck_view(battle.deck1))

    battle.team1_setup(move1)
    battle.team2_setup(move2)

    assert battle.team1_ready
    assert battle.team2_ready

    move1 = controller1.turn(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    while not battle.is_over():
        pass

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

    def __valid_setup(self, input_str:str, own_deck:OwnDeckView) -> bool:
        tokens = input_str.split(" ")
        indices = set()
        if tokens[0] == "play":
            for token in tokens[1:]:
                try:
                    t = int(token)
                except ValueError:
                    return False
                if t in indices:
                    return False
                indices.add(t)
                if t < 0 or t >= len(own_deck.hand) or not own_deck.hand[t].is_basic():
                    return False
            if len(tokens) > 1 and len(tokens) <= own_deck.bench_size + 2:
                return True
        return False
    
    def __parse_setup(self, input_str:str) -> tuple[int]:
        tokens = input_str.split(" ")
        return tuple([int(token) for token in tokens[1:]])

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> tuple[int]:
        user_input = input("Select your action (l for list of actions): ")
        while not self.__valid_setup(user_input, own_deck):
            match user_input:
                case "l":
                    print("l: list commands\nview own: View your own cards/deck setup\nview opp: View your opponent's cards/deck setup\n"+
                          "play x1 ... xn: Play the cards at index x1 and ... xn from your hand to the active spot")
                case "view own":
                    visualize_own_deck(own_deck)
                case "view opp":
                    visualize_opponent_deck(opponent_deck)
                case ["play", *_]:
                    print("invalid move")
                case _:
                    print("invalid command")
            user_input = input("Select your action: ")
        return self.__parse_setup(user_input)
from pokemon_battle import Battle, OwnDeckView, OpponentDeckView, get_opponent_deck_view, get_own_deck_view
from print_visualizer import visualize_own_deck, visualize_opponent_deck, visualize_active_pokemon, visualize_card

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

    move1 = controller1.make_move(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    while not battle.is_over():
        pass

class BattleController:

    def __init__(self):
        pass

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> str:
        pass

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> str:
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

    def __validate_command(self, input_str:str, command:str, max_val:int) -> tuple[bool,int]:
        tokens = input_str.split(" ")
        command_tokens = command.split(" ")
        if not len(tokens) == len(command_tokens) + 1:
            return False
        for i in range(len(command_tokens)):
            if not tokens[i] == command_tokens[i]:
                return False, -1
        try:
            num = int(tokens[-1])
            if num > max_val:
                return False, num
            return True, num
        except ValueError:
            return False, -1

    def __prompt_command(self, user_input:str, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, additional_moves:str):
        match user_input:
            case "l":
                print("l: list commands\n"+\
                        "view own: View your own cards/deck setup\n"+\
                        "view opp: View your opponent's cards/deck setup\n"+\
                        "own hand x:   View the card at index x in your hand\n"+\
                        "own active x: View the card at index x in your active spots\n"+\
                        "opp active x: View the card at index x in your opponent's active spots\n"+\
                        additional_moves)
            case "view own":
                visualize_own_deck(own_deck)
            case "view opp":
                visualize_opponent_deck(opponent_deck)
            case str(x) if "own hand" in x:
                valid, index = self.__validate_command(user_input, "own hand", len(own_deck.hand))
                if valid:
                    visualize_card(own_deck.hand[index])
                else:
                    print("invalid command")
            case str(x) if "own active" in x:
                valid, index = self.__validate_command(user_input, "own active", len(own_deck.active))
                if valid:
                    visualize_active_pokemon(own_deck.active[index])
                else:
                    print("invalid command")
            case str(x) if "opp active" in x:
                valid, index = self.__validate_command(user_input, "opp active", len(opponent_deck.active))
                if valid:
                    visualize_active_pokemon(opponent_deck.active[index])
                else:
                    print("invalid command")
            case _:
                print("invalid command")

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> tuple[int]:
        user_input = input("Select your action (l for list of actions): ")
        while not self.__valid_setup(user_input, own_deck):
            self.__prompt_command(user_input, own_deck, opponent_deck, "play x1 ... xn: Play the cards at index x1 and ... xn from your hand to the active spot")
            user_input = input("Select your action: ")
        return self.__parse_setup(user_input)
    
    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> str:
        additional_moves = "play card x: ...\n"+\
                           "play basic x y: ...\n"+\
                           "evolve x y: ...\n"+\
                           "retreat x e1 ... en: ...\n"+\
                           "attack x: ...\n"+\
                           "use ability x: ...\n"+\
                           "select x: ...\n"+\
                           "place energy x: ...\n"
        user_input = input("Select your action (l for list of actions): ")
        while not self.__valid_setup(user_input, own_deck):
            self.__prompt_command(user_input, own_deck, opponent_deck, additional_moves)
            user_input = input("Select your action: ")
        return self.__parse_setup(user_input)
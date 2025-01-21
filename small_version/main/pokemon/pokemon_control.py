from pokemon.pokemon_battle import Battle, OwnDeckView, OpponentDeckView, get_opponent_deck_view, get_own_deck_view
from pokemon.print_visualizer import visualize_own_deck, visualize_opponent_deck, visualize_active_pokemon, visualize_card
from pokemon.pokemon_types import EnergyType, EnergyContainer

def battle_control(battle:Battle, controller1:'BattleController', controller2:'BattleController') -> None:
    """Controls the flow and inputs to a battle

    :param battle: The battle to control
    :type battle: Battle
    :param controller1: The controller for team 1
    :type controller1: BattleController
    :param controller2: The controller for team 2
    :type controller2: BattleController
    """
    print("The battle has begun")

    print("Team 1 set up your cards")
    move1 = controller1.setup_cards(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    while not battle.valid_setup(move1, battle.deck1):
        print("\nInvalid move, Team 1 set up your cards")
        move1 = controller1.setup_cards(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    
    print("Team 2 set up your cards")
    move2 = controller2.setup_cards(get_own_deck_view(battle.deck2), get_opponent_deck_view(battle.deck1))
    while not battle.valid_setup(move2, battle.deck2):
        print("\nInvalid move, Team 2 set up your cards")
        move2 = controller2.setup_cards(get_own_deck_view(battle.deck2), get_opponent_deck_view(battle.deck1))

    assert battle.team1_setup(move1)
    assert battle.team2_setup(move2)

    print("Team 1, it's your turn")
    move, inputs = controller1.make_move(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
    while not battle.is_over():
        match move:
            case "play_card":
                success = battle.play_card(*inputs)
            case "play_basic":
                success = battle.play_basic(*inputs)
            case "evolve":
                success = battle.evolve(*inputs)
            case "retreat":
                success = battle.retreat(*inputs)
            case "attack":
                success = battle.attack(*inputs)
            case "use_ability":
                success = battle.use_ability(*inputs)
            case "select":
                success = battle.select(*inputs)
            case "place_energy":
                success = battle.place_energy(*inputs)
            case "end_turn":
                success = battle.end_turn()
        if not success:
            print("Invalid move, try again")
            print(f"Try one of these: {battle.available_actions()}")
        if battle.team1_move():
            print("Team 1, it's your move")
            move, inputs = controller1.make_move(get_own_deck_view(battle.deck1), get_opponent_deck_view(battle.deck2))
        else:
            print("Team 2, it's your turn")
            move, inputs = controller2.make_move(get_own_deck_view(battle.deck2), get_opponent_deck_view(battle.deck1))
    print("Battle is over")

class BattleController:

    def __init__(self):
        pass

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> tuple[int]:
        pass

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> tuple[str,tuple[int|EnergyType]]:
        pass

class CommandLineBattleController(BattleController):

    def __init__(self):
        super().__init__()

    def __valid_setup(self, input_str:str, own_deck:OwnDeckView) -> bool:
        error_checking=False
        tokens = input_str.split(" ")
        if error_checking:
            indices = set()
        if tokens[0] == "play":
            for token in tokens[1:]:
                try:
                    t = int(token)
                except ValueError:
                    return False
                if error_checking:
                    if t in indices:
                        return False
                    indices.add(t)
                    if t < 0 or t >= len(own_deck.hand) or not own_deck.hand[t].is_basic():
                        return False
            if (not error_checking and len(tokens) > 1) or (len(tokens) > 1 and len(tokens) <= own_deck.bench_size + 2):
                return True
        return False
    
    def __parse_setup(self, input_str:str) -> tuple[int]:
        tokens = input_str.split(" ")
        return tuple([int(token) for token in tokens[1:]])

    def __validate_command(self, input_str:str, command:str, max_val:int) -> tuple[bool,int]:
        tokens = input_str.split(" ")
        command_tokens = command.split(" ")
        if not len(tokens) == len(command_tokens) + 1:
            return False, -1
        for i in range(len(command_tokens)):
            if not tokens[i] == command_tokens[i]:
                return False, -1
        try:
            num = int(tokens[-1])
            if num < 0 or num >= max_val:
                return False, num
            return True, num
        except ValueError:
            return False, -1

    def __prompt_command(self, user_input:str, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, additional_moves:dict[str,str]):
        action_descs = {
            'l':            'list commands',
            'actions':      'List the available actions',
            'view_own':     'View your own cards/deck setup',
            'view_opp':     "View your opponent's cards/deck setup",
            'own_hand x':   'View the card at index x in your hand',
            'own_active x': 'View the card at index x in your active spots',
            'opp_active x': "View the card at index x in your opponent's active spots"
        }
        match user_input:
            case "l":
                for action, description in action_descs.items():
                    print(f"{action:20}: {description}")
                for action, description in additional_moves.items():
                    print(f"{action:20}: {description}")
            case 'actions':
                print("TODO: this :(")
            case "view_own":
                visualize_own_deck(own_deck)
            case "view_opp":
                visualize_opponent_deck(opponent_deck)
            case str(x) if "own_hand" in x:
                valid, index = self.__validate_command(user_input, "own_hand", len(own_deck.hand))
                if valid:
                    visualize_card(own_deck.hand[index])
                else:
                    print("invalid command")
            case str(x) if "own_active" in x:
                valid, index = self.__validate_command(user_input, "own_active", len(own_deck.active))
                if valid:
                    visualize_active_pokemon(own_deck.active[index])
                else:
                    print("invalid command")
            case str(x) if "opp_active" in x:
                valid, index = self.__validate_command(user_input, "opp_active", len(opponent_deck.active))
                if valid:
                    visualize_active_pokemon(opponent_deck.active[index])
                else:
                    print("invalid command")
            case _:
                print("invalid command")

    def setup_cards(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> tuple[int]:
        user_input = input("\nSelect your action (l for list of actions): ")
        while not self.__valid_setup(user_input, own_deck):
            self.__prompt_command(user_input, own_deck, opponent_deck, {"play x1 ... xn": "Play the cards at index x1 and ... xn from your hand to the active spot"})
            user_input = input("\nSelect your action: ")
        return self.__parse_setup(user_input)
    
    def __validate_move(self, input_str:str) -> tuple[bool,str,tuple|str]:
        tokens = input_str.split(" ")
        match tokens[0]:
            case "play_card":
                if len(tokens) == 2:
                    try:
                        hand_index = int(tokens[1])
                    except ValueError:
                        return False, "play_card", "requires int"
                    return True, "play_card", (hand_index,)
                return False, "play_card", "requires one argument"
            case "play_basic":
                if len(tokens) == 2:
                    try:
                        hand_index = int(tokens[1])
                    except ValueError:
                        return False, "play_basic", "requires int"
                    return True, "play_basic", (hand_index,)
                return False, "play_basic", "requires one argument"   
            case "evolve":
                if len(tokens) == 3:
                    try:
                        hand_index =   int(tokens[1])
                        active_index = int(tokens[2])
                    except ValueError:
                        return False, "evolve", "requires 2 ints"
                    return True, "evolve", (hand_index, active_index)
                return False, "evolve", "requires 2 arguments"                    
            case "retreat":
                if len(tokens) >= 2:
                    try:
                        active_index = int(tokens[1])
                    except ValueError:
                        return False, "retreat", "first arg is int"
                    energies = EnergyContainer()
                    for token in tokens[2:]:
                        if token.upper() in EnergyType:
                            energies = energies.add_energy(EnergyType[token.upper()])
                        else:
                            return False, "retreat", f"invalid energy type: {token}"
                    return True, "retreat", (active_index, energies)
                return False, "retreat", "requires at least 2 arguments"
            case "attack":
                if len(tokens) == 2:
                    try:
                        attack_index = int(tokens[1])
                    except ValueError:
                        return False, "attack", "requires an int"
                    return True, "attack", (attack_index,)
                return False, "attack", "requires an argument"
            case "use_ability":
                if len(tokens) == 3:
                    try:
                        active_index  = int(tokens[1])
                        ability_index = int(tokens[2])
                    except ValueError:
                        return False, "use_ability", "requires two ints"
                    return True, "use_ability", (active_index, ability_index)
                return False, "use_ability", "requires an argument"
            case "select":
                if len(tokens) == 2:
                    try:
                        index = int(tokens[1])
                    except ValueError:
                        return False, "select", "requires an int"
                    return True, "select", (index,)
                return False, "select", "requires an argument"
            case "place_energy":
                if len(tokens) == 2:
                    try:
                        active_index = int(tokens[1])
                    except ValueError:
                        return False, "place_energy", "requires an int"
                    return True, "place_energy", (active_index,)
                return False, "place_energy", "requires an argument"
            case "end_turn":
                if len(tokens) == 1:
                    return True, "end_turn", (None,)
                return False, "end_turn", "requires no arguments"
            case _:
                return False, "", ""

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView) -> str:
        additional_moves = {
            "play_card x":         "...",
            "play_basic x":      "...",
            "evolve x y":          "...",
            "retreat x e1 ... en": "...",
            "attack x":            "...",
            "use_ability x":       "...",
            "select x":            "...",
            "place_energy x":      "...",
            "end_turn":            "..."
        }
        user_input = input("\nSelect your action (l for list of actions): ")
        valid, move, inputs = self.__validate_move(user_input)
        while not valid:
            print(f"{move} error: {inputs}")
            self.__prompt_command(user_input, own_deck, opponent_deck, additional_moves)
            user_input = input("\nSelect your action: ")
            valid, move, inputs = self.__validate_move(user_input)
        return move, inputs
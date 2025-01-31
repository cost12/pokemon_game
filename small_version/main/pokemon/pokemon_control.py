from pokemon.pokemon_battle import Battle, Action, Rules, OwnDeckView, OpponentDeckView, get_opponent_deck_view, get_own_deck_view
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
    action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score())
    inputs = (True, *inputs)
    while not battle.action(action, inputs):
        print("\nInvalid move, Team 1 set up your cards")
        action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score())
        inputs = (True, *inputs)
    
    print("Team 2 set up your cards")
    action, inputs = controller2.make_move(get_own_deck_view(battle.state.deck2), get_opponent_deck_view(battle.state.deck1), battle.available_actions(), battle.get_rules(), battle.get_score())
    inputs = (False, *inputs)
    while not battle.action(action, inputs):
        print("\nInvalid move, Team 2 set up your cards")
        action, inputs = controller2.make_move(get_own_deck_view(battle.state.deck2), get_opponent_deck_view(battle.state.deck1), battle.available_actions(), battle.get_rules(), battle.get_score())
        inputs = (False, *inputs)

    print("Team 1, it's your turn")
    action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score())
    while not battle.is_over():
        success = battle.action(action, inputs)
        if not success:
            print("Invalid move, try again")
        if battle.team1_move():
            print("Team 1, it's your move")
            action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score())
        else:
            print("Team 2, it's your turn")
            action, inputs = controller2.make_move(get_own_deck_view(battle.state.deck2), get_opponent_deck_view(battle.state.deck1), battle.available_actions(), battle.get_rules(), battle.get_score())
    print("Battle is over")

class BattleController:

    def __init__(self):
        pass

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, available_actions:dict[str,Action], rules:Rules, score:tuple[int]) -> tuple[str,tuple[int|EnergyType]]:
        pass

class CommandLineBattleController(BattleController):

    def __init__(self):
        super().__init__()

    def __prompt_command(self, user_input:str, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, action_descs:dict[str,str], available_actions:dict[str,Action], score:tuple[int]) -> tuple[bool,str,tuple]:
        tokens = user_input.split(" ")
        if tokens[0] in available_actions:
            valid, inputs = available_actions[tokens[0]].is_valid_raw(tokens[1:])
            if valid:
                return True, tokens[0], inputs
        match tokens[0]:
            case "l":
                for action, description in action_descs.items():
                    print(f"{action:20}: {description}")
                for name, action in available_actions.items():
                    print(f"{action.input_format():20}: {action.action_description()}")
            case "score":
                print(f"Team1: {score[0]} Team2: {score[0]}")
            case "view_own":
                visualize_own_deck(own_deck)
            case "view_opp":
                visualize_opponent_deck(opponent_deck)
            case "own_hand":
                if len(tokens) == 2:
                    try:
                        index = int(tokens[1])
                    except ValueError:
                        return False, None, None
                    if index >= 0 and index < len(own_deck.hand):
                        visualize_card(own_deck.hand[index])
                else:
                    print("invalid command")
            case "own_active":
                if len(tokens) == 2:
                    try:
                        index = int(tokens[1])
                    except ValueError:
                        return False, None, None
                    if index >= 0 and index < len(own_deck.active):
                        visualize_active_pokemon(own_deck.active[index])
                else:
                    print("invalid command")
            case "opp_active":
                if len(tokens) == 2:
                    try:
                        index = int(tokens[1])
                    except ValueError:
                        return False, None, None
                    if index >= 0 and index < len(opponent_deck.active):
                        visualize_active_pokemon(opponent_deck.active[index])
                else:
                    print("invalid command")
            case _:
                print("invalid command")
        return False, None, None

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, available_actions:dict[str,Action], rules:Rules, score:tuple[int]) -> tuple[str,tuple[int|EnergyType]]:
        action_descs = {
            'l':            'list valid commands',
            'score':        "View the score",
            'view_own':     'View your own cards/deck setup',
            'view_opp':     "View your opponent's cards/deck setup",
            'own_hand x':   'View the card at index x in your hand',
            'own_active x': 'View the card at index x in your active spots',
            'opp_active x': "View the card at index x in your opponent's active spots"
        }
        user_input = input("\nSelect your action (l for list of actions): ")
        valid, move, inputs = self.__prompt_command(user_input, own_deck, opponent_deck, action_descs, available_actions, score)
        while not valid:
            user_input = input("\nSelect your action: ")
            valid, move, inputs = self.__prompt_command(user_input, own_deck, opponent_deck, action_descs, available_actions, score)
        return move, inputs
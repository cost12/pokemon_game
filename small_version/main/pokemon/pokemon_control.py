from pokemon.pokemon_battle import Battle, Action, Rules, OwnDeckView, OpponentDeckView, get_opponent_deck_view, get_own_deck_view, UserInput
from pokemon.print_visualizer import visualize_own_deck, visualize_opponent_deck, visualize_active_pokemon, visualize_card
from pokemon.pokemon_types import EnergyType

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
    action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
    inputs = (True, *inputs)
    while not battle.action(action, inputs):
        print("\nInvalid move, Team 1 set up your cards")
        action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
        inputs = (True, *inputs)
    
    print("Team 2 set up your cards")
    action, inputs = controller2.make_move(get_own_deck_view(battle.state.deck2), get_opponent_deck_view(battle.state.deck1), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
    inputs = (False, *inputs)
    while not battle.action(action, inputs):
        print("\nInvalid move, Team 2 set up your cards")
        action, inputs = controller2.make_move(get_own_deck_view(battle.state.deck2), get_opponent_deck_view(battle.state.deck1), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
        inputs = (False, *inputs)

    print("Team 1, it's your turn")
    action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
    while not battle.is_over():
        success = battle.action(action, inputs)
        if not success:
            print("Invalid move, try again")
        if battle.team1_move():
            print("Team 1, it's your move")
            action, inputs = controller1.make_move(get_own_deck_view(battle.state.deck1), get_opponent_deck_view(battle.state.deck2), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
        else:
            print("Team 2, it's your turn")
            action, inputs = controller2.make_move(get_own_deck_view(battle.state.deck2), get_opponent_deck_view(battle.state.deck1), battle.available_actions(), battle.get_rules(), battle.get_score(), battle.get_partial_inputs())
    print("Battle is over")

class BattleController:

    def __init__(self):
        pass

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, available_actions:dict[str,Action], rules:Rules, score:tuple[int], partial_inputs:tuple) -> tuple[str,tuple[int|EnergyType]]:
        pass


class CommandLineAction:
    def action_name(self) -> str:
        pass

    def action_description(self) -> str:
        pass

    def input_format(self) -> str:
        pass

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,'CommandLineAction'], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        pass

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,'CommandLineAction'], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        pass

class ListAction(CommandLineAction):
    def action_name(self) -> str:
        return 'list'

    def action_description(self) -> str:
        return 'list valid commands'

    def input_format(self) -> str:
        return 'list (x)'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        return len(inputs) == 0 or inputs[0] in ['actions','views'], inputs

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        if len(inputs) == 0 or inputs[0] == 'views':
            for _, action in commandline_actions.items():
                print(f"{action.input_format():20}: {action.action_description()}")
        if len(inputs) == 0 or inputs[0] == 'actions':
            for _, action in available_actions.items():
                print(f"{action.input_format():20}: {action.action_description()}")

class ScoreAction(CommandLineAction):
    def action_name(self) -> str:
        return 'score'

    def action_description(self) -> str:
        return 'View the score'

    def input_format(self) -> str:
        return 'score'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        return len(inputs) == 0, tuple()

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        print(f"Team1: {score[0]} Team2: {score[1]}")

class ViewOwnSetupAction(CommandLineAction):
    def action_name(self) -> str:
        return 'view_own'

    def action_description(self) -> str:
        return 'View your own cards/deck setup'

    def input_format(self) -> str:
        return 'view_own'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        return len(inputs) == 0, tuple()

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        visualize_own_deck(own_deck)

class ViewOpponentSetupAction(CommandLineAction):
    def action_name(self) -> str:
        return 'view_opp'

    def action_description(self) -> str:
        return "View your opponent's cards/deck setup"

    def input_format(self) -> str:
        return 'view_opp'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        return len(inputs) == 0, tuple()

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        visualize_opponent_deck(opponent_deck)

class ViewOwnHandAction(CommandLineAction):
    def action_name(self) -> str:
        return 'own_hand'

    def action_description(self) -> str:
        return 'View a specific card in your hand'

    def input_format(self) -> str:
        return 'own_hand x'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                index = int(inputs[0])
            except ValueError:
                return False, None
            if index >= 0 and index < len(own_deck.hand):
                return True, (index,)
        return False, None

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        visualize_card(own_deck.hand[inputs[0]])

class ViewOwnActiveAction(CommandLineAction):
    def action_name(self) -> str:
        return 'own_active'

    def action_description(self) -> str:
        return 'View a specific card in your active area'

    def input_format(self) -> str:
        return 'own_active x'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                index = int(inputs[0])
            except ValueError:
                return False, None
            if index >= 0 and index < len(own_deck.active):
                return True, (index,)
        return False, None

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        visualize_active_pokemon(own_deck.active[inputs[0]])

class ViewOpponentActiveAction(CommandLineAction):
    def action_name(self) -> str:
        return 'opp_active'

    def action_description(self) -> str:
        return "View a specific card in your opponent's active area"

    def input_format(self) -> str:
        return 'opp_active x'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        if len(inputs) == 1:
            try:
                index = int(inputs[0])
            except ValueError:
                return False, None
            if index >= 0 and index < len(opponent_deck.active):
                return True, (index,)
        return False

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        visualize_active_pokemon(opponent_deck.active[inputs[0]])

class SelectInfoAction(CommandLineAction):
    def action_name(self) -> str:
        return 'select_info'

    def action_description(self) -> str:
        return "If select action is available, see what you are selecting for"

    def input_format(self) -> str:
        return 'select_info'

    def is_valid_raw(self, inputs:tuple[str], own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool, tuple]:
        return len(inputs) == 0, tuple()

    def action(self, inputs:tuple, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> None:
        if partial_inputs is None:
            print("Nothing to select")
        elif isinstance(partial_inputs[0], UserInput):
            print(partial_inputs[0].prompt)


class CommandLineBattleController(BattleController):

    def __init__(self, name:str):
        super().__init__()
        self.name = name

    def __prompt_command(self, user_input:str, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, commandline_actions:dict[str,CommandLineAction], available_actions:dict[str,Action], score:tuple[int], partial_inputs:tuple) -> tuple[bool,str,tuple]:
        tokens = user_input.split(" ")
        if 0 and partial_inputs is not None:
            tokens = (tokens[0], *partial_inputs, *tokens[1:])
        if tokens[0] in available_actions:
            valid, inputs = available_actions[tokens[0]].is_valid_raw(tokens[1:] if partial_inputs is None else (*partial_inputs, *tokens[1:]))
            if valid:
                return True, tokens[0], inputs
            else:
                print(f"Invalid inputs for {tokens[0]}")
        if tokens[0] in commandline_actions:
            valid, inputs = commandline_actions[tokens[0]].is_valid_raw(tokens[1:], own_deck, opponent_deck, commandline_actions, available_actions, score, partial_inputs)
            if valid:
                commandline_actions[tokens[0]].action(inputs, own_deck, opponent_deck, commandline_actions, available_actions, score, partial_inputs)
            else:
                print("Invalid command, try list to see all commands")
        return False, None, None

    def make_move(self, own_deck:OwnDeckView, opponent_deck:OpponentDeckView, available_actions:dict[str,Action], rules:Rules, score:tuple[int], partial_inputs:tuple) -> tuple[str,tuple[int|EnergyType]]:
        commands = list[CommandLineAction]([
            ListAction(),
            ScoreAction(),
            ViewOwnSetupAction(),
            ViewOpponentSetupAction(),
            ViewOwnHandAction(),
            ViewOwnActiveAction(),
            ViewOpponentActiveAction(),
            SelectInfoAction(),
        ])
        commandline_actions = {action.action_name():action for action in commands}
        user_input = input(f"\n{self.name}, select your action: ")
        valid, move, inputs = self.__prompt_command(user_input, own_deck, opponent_deck, commandline_actions, available_actions, score, partial_inputs)
        while not valid:
            user_input = input(f"\n{self.name}, select your action: ")
            valid, move, inputs = self.__prompt_command(user_input, own_deck, opponent_deck, commandline_actions, available_actions, score, partial_inputs)
        return move, inputs

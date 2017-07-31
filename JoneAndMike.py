from Player import Player

class JoneAndMike(Player):
    def __init__(self, position):
        self.position = position

    def pass_card(self, gamestate):
        """ returns the index of the card to pass """
        raise Exception('Unimplemented pass_card')

    def guess_card(self, gamestate):
        """ returns a tuple (pid, ind, guess), which is equivalent to guessing the indth card of pid as guess """
        raise Exception('Unimplemented guess')

    def flip_card(self, gamestate):
        """ returns the index of the card to flip """
        raise Exception('Unimplemented flip')

    def claim(self, gamestate):
        """ returns a tuple (claiming, cards) of a boolean and a list of list """
        """ bool: true or false, whether the player wants to claim """
        """ list of list: structure which contains all the correct answers """
        raise Exception('Unimplemented claim')

    def get_internal_gamestate(self, gamestate):
        """given an external gamestate, updates internal gamestate"""
        hi = [[(set(range(12)),0) for j in range(6)] for i in range(4)]

    def num_possible_configs(self, internal_gamestate):
        """given an Internal Gamestate structure, calculates number of possible configs"""
        pass

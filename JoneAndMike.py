from Player import Player
from copy import deepcopy
import pprint
from GameState import GameState

import random

class JoneAndMike(Player):
    def __init__(self, position):
        self.position = position

    def pass_card(self, gamestate):
        """ returns the index of the card to pass """
        raise Exception('Unimplemented pass_card')

    def guess_card(self, gamestate):
        deduction = self.get_deductions(gamestate.cards)

        guesses = []
        for i in [(self.position+1)%4, (self.position+3)%4]:
            for j in range(6):
                num_pos = len(deduction[i][j][0])
                if num_pos != 1:
                    guesses.append((num_pos, i, j, list(deduction[i][j][0])[random.randint(0,3)]))

        guesses.sort()

        print(guesses)

        return (guesses[0][1], guesses[0][2], guesses[0][3])


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

    def get_deductions(self, gamestate):
        """given an external gamestate, updates internal gamestate"""
        deduction = [[[set(range(12)),0] for j in range(6)] for i in range(4)]

        for i in range(4):
            for j in range(6):
                deduction[i][j][1] = gamestate[i][j]['color']

                if gamestate[i][j]['rank'] != 'Unclear':
                    deduction[i][j][0] = set([gamestate[i][j]['rank']])

        old_deduction = deepcopy(deduction)
        deduction = self.do_deduction(deduction)
        while old_deduction != deduction:
            old_deduction = deepcopy(deduction)
            deduction = self.do_deduction(deduction)

        pp = pprint.PrettyPrinter(indent=4)
        print(pprint.pformat(deduction))

        return deduction


    def do_deduction(self, deduction):
        # Increasing
        for i in range(4):
            mins = [-1, -1]
            for j in range(6):
                for num in deepcopy(deduction[i][j][0]):
                    if num <= mins[deduction[i][j][1]] or num < mins[(deduction[i][j][1]+1)%2]:
                        deduction[i][j][0].remove(num)
                        # print("Hand %d Card %d can't be %d because it must be greater" % (i, j, num))
                mins[deduction[i][j][1]] = min(deduction[i][j][0]) 

        # Decreasing
        for i in range(4):
            maxs = [12, 12]
            for j in reversed(range(6)):
                for num in deepcopy(deduction[i][j][0]):
                    if num >= maxs[deduction[i][j][1]] or num > maxs[(deduction[i][j][1]+1)%2]:
                        deduction[i][j][0].remove(num)
                        # print("Hand %d Card %d can't be %d because it must be smaller" % (i, j, num))

                maxs[deduction[i][j][1]] = max(deduction[i][j][0]) 

        # Uniqueness
        for i in range(4):
            for j in range(6):
                if len(deduction[i][j][0]) == 1:
                    only_number = list(deduction[i][j][0])[0]
                    for k in range(4):
                        for l in range(6):
                            if not (i == k and j == l):
                                if deduction[i][j][1] == deduction[k][l][1] and only_number in deduction[k][l][0]:
                                    deduction[k][l][0].remove(only_number)
                                    # print("Hand %d Card %d can't be %d because it already exists somewhere" % (i, j, num))

        # Existence
        for rank in range(12):
            for color in range(2):
                instances = 0
                person = -1
                card = -1

                for i in range(4):
                    for j in range(6):
                        if rank in deduction[i][j][0] and color == deduction[i][j][1]:
                            instances += 1
                            person = i
                            card = j

                assert instances != 0
                if instances == 1:
                    # if len(deduction[person][card][0]) > 1:
                    #     print("Hand %d Card %d must be %d because it's the only card that can be" % (person, card, rank))
                    deduction[person][card][0] = set([rank])



        return deduction


    def num_possible_configs(self, internal_gamestate):
        """given an Internal Gamestate structure, calculates number of possible configs"""
        pass


if __name__ == '__main':
    jam = JoneAndMike(0)

    jam.get_deductions([   [   {'color': 1, 'rank': 0},
            {'color': 1, 'rank': 1},
            {'color': 0, 'rank': 2},
            {'color': 0, 'rank': 4},
            {'color': 1, 'rank': 8},
            {'color': 1, 'rank': 11}],
        [   {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'}],
        [   {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'}],
        [   {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'}]])

    cards = [   [   {'color': 1, 'rank': 0},
            {'color': 1, 'rank': 1},
            {'color': 0, 'rank': 2},
            {'color': 0, 'rank': 4},
            {'color': 1, 'rank': 8},
            {'color': 1, 'rank': 11}],
        [   {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'}],
        [   {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'}],
        [   {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'},
            {'color': 1, 'rank': 'Unclear'},
            {'color': 0, 'rank': 'Unclear'}]]

    gs = GameState(cards=cards, player=0)

    print(jam.guess_card(gs))


    # jam.get_internal_gamestate([   [   {'color': 1, 'rank': 0},
    #         {'color': 1, 'rank': 1},
    #         {'color': 0, 'rank': 2},
    #         {'color': 0, 'rank': 4},
    #         {'color': 1, 'rank': 8},
    #         {'color': 1, 'rank': 11}],
    #     [   {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'}],
    #     [   {'color': 0, 'rank': 1},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'}],
    #     [   {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'},
    #         {'color': 1, 'rank': 'Unclear'},
    #         {'color': 0, 'rank': 'Unclear'}]])
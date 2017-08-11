from Action import Action
from GameState import GameState
from ManualAI import ManualAI

import random

class Game:
    def __init__(self, AIs, debug = False):
        self.gs = GameState()
        self.turn = random.randint(0, 3)

        self.pgs = []
        for i in range(4):
            self.pgs.append(GameState(self.gs.cards, i))

        self.AIs = AIs
        self.debug = debug
        self.is_game_over = False
        self.score = [0]*4

    def run_game(self):
        while not self.is_game_over:
            self.play_turn()
        return self.score

    def check_claims(self):
        players = list(range(4))
        random.shuffle(players)

        for player in players:
            is_claiming, cards = self.AIs[player].claim(self.pgs[player])

            if is_claiming:
                self.do_claim(player, cards)
                return True

        return False

    def play_turn(self):
        which_card = self.AIs[self.turn].pass_card(self.pgs[self.turn])
        self.do_pass(which_card)

        if self.check_claims():
            return

        friend = (self.turn+2)%4
        which_player, which_card, guess = self.AIs[friend].guess_card(self.pgs[friend])
        correct = self.do_guess(which_player, which_card, guess)

        if self.check_claims():
            return

        if not correct:
            which_card = self.AIs[friend].flip_card(self.pgs[friend])
            self.do_flip(which_card)

            if self.check_claims():
                return

        self.turn = (self.turn + 1) % 4

    def update_history(self, action):
        self.gs.history.append(action)

        for i in range(4):
            self.pgs[i].history.append(action)

    def do_pass(self, which_card):
        from_player = self.turn
        receive_player = (self.turn+2)%4

        self.check_input(which_card >= 0 and which_card < 6, ("Cannot pass the %dth card" % which_card))

        should_check = False
        for i in xrange(6):
            if self.pgs[receive_player].cards[from_player][i]['rank'] == 'Unclear':
                should_check = True
                break
        if should_check:
            # print "checking pass", [self.pgs[receive_player].cards[from_player][i]['rank'] for i in xrange(6)]
            self.check_input(self.pgs[receive_player].cards[from_player][which_card]['rank'] == 'Unclear', \
                   ("Cannot pass the %dth card, as it has already been passed" % which_card))

        self.pgs[receive_player].cards[from_player][which_card] = self.gs.cards[from_player][which_card]

        action = Action("pass", player=self.turn, which_card=which_card)
        self.update_history(action)

    def do_guess(self, which_player, which_card, guess):
        guessing_player = (self.turn+2)%4

        self.check_input(which_player >= 0 and which_player < 4, ("Does not exist an %dth player" % which_player))
        self.check_input(which_card >= 0 and which_card < 6, ("Cannot guess the %dth card" % which_card))
        self.check_input(guess >= 0 and guess < 12, ("Cannot guess that a card is %d" % guess))
        self.check_input((guessing_player - which_player) % 2 != 0, "Can't guess a card of your friend")

        should_check = False
        for i in xrange(6):
            if self.pgs[guessing_player].cards[which_player][i]['rank'] == 'Unclear':
                should_check = True
                break
        if not should_check:
            for i in xrange(6):
                if self.pgs[guessing_player].cards[(which_player + 2) % 4][i]['rank'] == 'Unclear':
                    should_check = True
                    break
        if should_check:
            # print "checking guess", [self.pgs[guessing_player].cards[which_player][i]['rank'] for i in xrange(6)], [self.pgs[guessing_player].cards[(which_player + 2) % 4][i]['rank'] for i in xrange(6)]

            self.check_input(self.pgs[guessing_player].cards[which_player][which_card]['rank'] == 'Unclear', \
                    "Cannot guess the %dth card, as it has already been revealed" % which_card)

        is_correct = self.gs.cards[which_player][which_card]['rank'] == guess

        if is_correct:
            for i in range(4):
                self.pgs[i].cards[which_player][which_card] = self.gs.cards[which_player][which_card]

        action = Action("guess", player=guessing_player, which_card=which_card, which_player=which_player, guess=guess, is_correct=is_correct)
        self.update_history(action)

        return is_correct

    def do_flip(self, which_card):
        flip_player = (self.turn+2)%4

        self.check_input(which_card >= 0 and which_card < 6, ("Cannot pass the %dth card" % which_card))

        should_check = False
        for i in xrange(6):
            if self.pgs[(flip_player + 1) % 4].cards[flip_player][i]['rank'] == 'Unclear':
                should_check = True
                break
        if should_check:
            # print "checking flip", [self.pgs[(flip_player + 1) % 4].cards[flip_player][i]['rank'] for i in xrange(6)]
            self.check_input(self.pgs[(flip_player + 1) % 4].cards[flip_player][which_card]['rank'] == 'Unclear', \
                "Cannot flip the %dth card, as it has already been flipped" % which_card)

        for i in range(4):
            self.pgs[i].cards[flip_player][which_card] = self.gs.cards[flip_player][which_card]

        action = Action("flip", player=flip_player, which_card=which_card)
        self.update_history(action)

    def do_claim(self, player, cards):
        self.is_game_over = True

        self.turn = player
        self.check_input(all(all(card >= 0 and card < 12 for card in hand) for hand in cards), \
                    "Cannot claim an out of range card")

        for i in range(4):
            for j in range(6):
                if cards[i][j] != self.gs.cards[i][j]['rank']:
                    raise Exception("incorrect claim")
                    self.score = self.score_with_winner((player+1)%4)
                    return

        self.score = self.score_with_winner(player)

    def check_input(self, condition, message):
        if not condition:
            if self.debug:
                import sys;sys.exit(">>> Error: %s <<<" % message)
            else:
                raise RuntimeError(self.score_with_winner((self.turn + 1) % 4),message)

    def score_with_winner(self, winner):
        score = [0] * 4
        score[winner] = 1
        score[(winner+2)%4] = 1
        return score
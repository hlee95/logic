class Action:
    def __init__(self, action, player, which_card, which_player=None, guess=None, cards=None, is_correct=None):
        self.action = action
        self.player = player
        self.which_player = which_player
        self.which_card = which_card
        self.guess = guess
        self.is_correct = is_correct

    def __str__(self):
        if self.action == "pass":
            return "Pass from Player %d to Player %d the %dth card" % (self.player, (self.player + 2) % 4, self.which_card)
        elif self.action == "guess":
            return "Guess from Player %d that Player %d's %dth card is %d is %r" % (self.player, self.which_player, self.which_card, self.guess, self.is_correct)
        elif self.action == "flip":
            return "Flip from Player %d revealing their %dth card" % (self.player, self.which_card)
        else:
            return "WAT"

    def __repr__(self):
        return self.__str__()

from GameState import GameState
from Action import Action
from Player import Player

from copy import deepcopy
import random

class HannaLarryPlayer(Player):
  def __init__(self, position):
    self.NUM_PLAYERS = 4
    self.CARDS_PER_PLAYER = 6
    self.NUM_RANKS = 12
    self.NUM_CARDS = 24
    self.me = position
    self.teammate = (self.me + 2) % self.NUM_PLAYERS
    # Save time by not updating our stuff until we actually need to make a move
    # or until there have been enough moves that we can maybe actually claim.
    # Also, don't claim if the last action was ours I think? Idk.
    self.num_turns = 0
    # Two level map. Position is 0 - 23.
    # Position 13 means player 13 / 6 = 2, card 13 % 6 = 1.
    # Map position to a dictionary of ranks 0 - 23 to their probability.
    self.distribution = self.empty_dict()
    # Keep track of +/- likelihoods.
    self.heuristics = self.empty_dict()
    # Keep track of what we can flip, pass and guess.
    self.flippable = range(self.CARDS_PER_PLAYER)
    self.passable = range(self.CARDS_PER_PLAYER)
    self.guessable = self.get_opponent_positions()
    ### For debugging.
    self.flipped = [] # what we have flipped
    self.all_revealed = [] # everything that's been revealed about opponents via other peoples' flips or correct guesses
    self.passed = [] # what we have passed
    self.guessed = [] # what we have guessed
    ###
    self.wrong_guesses = self.empty_dict()
    self.known_cards = self.empty_array()
    # So that we know which actions from the history we need to consider.
    self.next_action_idx = 0

    # possible configurations and likelihood
    # should have a density map to make the best guess
    # should also just know what all possible configurations are
    #   not sure if we can keep all of that in memory but idk maybe
    self.configurations = {}

  def pass_card(self, gamestate):
    """
    Choose to pass the card that gives the most information.
    """
    print "{} passing card".format(self.me)
    self.process_gamestate(gamestate)
    if len(self.passable) > 0:
      which_card = random.choice(self.passable)
      self.passable.remove(which_card)
      self.passed.append(which_card)
    else:
      which_card = 0
    return which_card

  def guess_card(self, gamestate):
    """
    Choose to guess that card with highest likelihood.
    """
    print "{} guessing card".format(self.me)
    self.process_gamestate(gamestate)
    # Get positions corresponding to opponents' cards.
    # TODO: Iterate through the distribution and guess the most likely card.
    # Make sure to only guess from the opponents' hands.
    pos = random.choice(self.guessable)
    print self.guessable
    print self.guessed
    print self.all_revealed
    self.guessable.remove(pos)
    print gamestate.cards
    self.guessed.append(pos)
    print pos
    return (pos[0], pos[1], random.choice(range(self.NUM_RANKS)))

  def flip_card(self, gamestate):
    """
    Choose to flip the card that yields the least information.
    """
    print "{} flipping card".format(self.me)
    self.process_gamestate(gamestate)
    if len(self.flippable) > 0:
      which_card = random.choice(self.flippable)
      self.flippable.remove(which_card)
      if which_card in self.passable:
        self.passable.remove(which_card)
      self.flipped.append(which_card)
    else:
      which_card = 0
    return which_card

  def claim(self, gamestate):
    """
    Return a tuple (claiming, cards)
     - claiming is a boolean
     - cards is a list of lists of dictionaries {color: , rank: }
    """
    print "{} chance to claim".format(self.me)
    # Good idea: claim even if we are not 100% sure, because
    # we will win more on average? Maybe. Not yet.
    self.process_gamestate(gamestate)
    claim = []
    for i in xrange(self.NUM_PLAYERS):
      hand = []
      for j in xrange(self.CARDS_PER_PLAYER):
        found_possible_card = False
        for card, count in self.distribution[i][j].iteritems():
          if count > 0:
            if found_possible_card:
              return (False, [])
            else:
              found_possible_card = True
              hand.append(self.num_to_rank(card))
      claim.append(hand)
    print "{} is claiming ".format(self.me), claim
    return (True, claim)

  """ ----------------
      Update Functions
      ---------------- """

  def process_gamestate(self, gamestate):
    """
    Process a new gamestate. Called at the beginning of each move.
    """
    for i in xrange(self.next_action_idx, len(gamestate.history)):
      self.process_action(gamestate.history[i], gamestate.cards)
    self.next_action_idx = len(gamestate.history)
    self.known_cards = deepcopy(gamestate.cards)
    # Update the distribution.
    self.distribution = self.make_distribution(self.undict_cards(gamestate.cards))
    print "Current distribution:"
    self.pprint_distribution(self.distribution)

  def process_action(self, action, cards):
    """
    Updates our state based on an action that was taken.
    """
    # TODO: Update heuristics based on each action.
    # Also need to update incorrect guesses and stuff.
    if action.action_type == "pass":
      # They think this card gives the most information
      if action.player == self.me:
        pass
      else:
        # TODO: Do something haha.
        pass
    elif action.action_type == "guess":
      if action.is_correct:
        # Remove from our guessable list.
        if (action.which_player, action.which_card) in self.guessable:
          self.all_revealed.append((action.which_player, action.which_card))
          self.guessable.remove((action.which_player, action.which_card))
      else:
        wrong_guess = action.guess + self.NUM_RANKS * cards[action.which_player][action.which_card]["color"]
        self.wrong_guesses[action.which_player][action.which_card][wrong_guess] = True
    elif action.action_type == "flip":
      # TODO: They think that card is already known or not important? Do something with that information.
      # Remove from our guessable list.
      self.all_revealed.append((action.player, action.which_card))
      if (action.player, action.which_card) in self.guessable:
        self.guessable.remove((action.player, action.which_card))
    else:
      raise Exception("Received action with unknown type %s", action.action_type)

  """ -----------------
      Make Distribution
      ----------------- """

  def get_known_cards(self, cards):
    """
    Returns a set of all cards we know for sure.
    """
    known = set()
    for i in xrange(self.NUM_PLAYERS):
      for j in xrange(self.CARDS_PER_PLAYER):
        if cards[i][j] >= 0:
          known.add(cards[i][j])
    return known

  def initial_possibilities(self, card_index, value):
    """
    Produces an array of possible values for a card, purely by index and value (-2 to 23)

    card_index: Value from 0-5, a player's possible cards
    value: Value from -2 to 23 for the card.
    """
    # This means it's a known card, return a list just containing the value
    if value >= 0:
      return [value]

    # Indexes 0,1 can only be rank 0-9; 2,3 can only be 1-10; 4,5 can only be 2-11
    # Number of invalid = number of cards to one side / 2
    # (two colors available to fill up with max or lowest values respectively)
    invalid_right = (self.CARDS_PER_PLAYER - 1 - card_index) /2
    invalid_left = card_index / 2
    poss_values = [j for j in range(invalid_left, self.NUM_RANKS - invalid_right)]

    # If color is 1, add color shift to all values
    if value == -1:
      for i in xrange(len(poss_values)):
        poss_values[i] += self.NUM_RANKS

    return poss_values

  def make_distribution(self, game_board):
    """
    Iterates through all possible values and returns a 4x6 array of dicts

    This is the main entry method of the solver.

    game_board: 4x6 array of numbers, -2 to 23, representing all cards (known or unknown)

    return: a 4x6 array of dicts, {key: possible value (0-23), value: # of valid configs}
    """

    def reset(val):
      return -2 if self.num_to_color(val) == 0 else -1

    def iterate(current_index):
      """
      Go through and test all valid assignments of cards, counting them up.

      current_index: 0-23, determines which card we're on in canonical order (player, card)
      card_dicts: 4x6 array of dictionaries, mapping from possible value to enumerations
      game_board: the existing assignments of all cards for the overall iteration
      """
      # If we're at the max index, update counts and pop out
      max_index = self.NUM_PLAYERS * self.CARDS_PER_PLAYER
      if current_index == max_index:
        # print "Made it to max index!"
        for i in xrange(self.NUM_PLAYERS):
          for j in xrange(self.CARDS_PER_PLAYER):
            card_dicts[i][j][game_board[i][j]] += 1
        return

      # Convert to 2-d coordinates from flattened index
      i, j = self.idx_to_pos(current_index)
      possibilities = card_dicts[i][j].keys()
      # Special case - it's a known value, so we skip and keep iterating
      if len(possibilities) == 1:
        game_board[i][j] = possibilities[0]
        iterate(current_index + 1)
      # Otherwise we determine valid moves given the filter
      else:
        valid_plays = filter(i, j, possibilities)
        # print "{} Valid plays for {} {}:".format(self.me, i,j), valid_plays
        # Recurse on all valid plays
        for play in valid_plays:
          # Set game board to play and add to known cards, then recurse
          game_board[i][j] = play
          known_cards.add(play)
          iterate(current_index + 1)
          # Since this isn't an assured play, we reset its assignment after
          known_cards.remove(play)
          game_board[i][j] = reset(play)

    def filter(i, j, all_plays):
      """
      Returns a valid list of moves at a given index given the current board and possible plays.
      """
      valid_plays = []
      for play in all_plays:
        # print play,
        # Filter for duplicates
        if play in known_cards:
          # print "Filtered as duplicate:", play
          continue

        # Filter for wrong guesses
        guesses = self.wrong_guesses[i][j].keys()
        if play in guesses:
          # print "Filtered as wrong guess:", play
          continue

        valid = True
        # Filter for > < conditions
        players_cards = game_board[i]
        # Go to left
        for a in xrange(j-1, -1, -1):
          # If it's a known or assigned card
          if players_cards[a] >= 0:
            # If equal color, >= invalidates (can't be equal either)
            if self.num_to_color(players_cards[a]) == self.num_to_color(play):
              if self.num_to_rank(players_cards[a]) >= self.num_to_rank(play):
                # print "Filtered since index {} val {} >= {}:".format(
                #  a, self.num_to_rank(players_cards[a]), self.num_to_rank(play))
                valid = False
                break
            else:
              if self.num_to_rank(players_cards[a]) > self.num_to_rank(play):
                # print "Filtered as > condition left:", play
                valid = False
                break
        # Go to right
        for a in xrange(j+1, self.CARDS_PER_PLAYER):
          # If it's a known or assigned card
          if players_cards[a] >= 0:
            # If equal color, <= invalidates (can't be equal either)
            if self.num_to_color(players_cards[a]) == self.num_to_color(play):
              if self.num_to_rank(players_cards[a]) <= self.num_to_rank(play):
                # print "Filtered as <= condition right:", play
                valid = False
            else:
              if self.num_to_rank(players_cards[a]) < self.num_to_rank(play):
                # print "Filtered as < condition right:", play
                valid = False
        if not valid:
          continue

        # If it survives all the tests, it's a valid move
        valid_plays.append(play)

      return valid_plays

    known_cards = self.get_known_cards(game_board)
    # Initialize possibility dictionaries
    card_dicts = self.empty_dict()
    for i in xrange(self.NUM_PLAYERS):
      for j in xrange(self.CARDS_PER_PLAYER):
        possibilities = self.initial_possibilities(j, game_board[i][j])
        for possibility in possibilities:
          card_dicts[i][j][possibility] = 0

    # Iterate through keyset of every dictionary
    iterate(0)
    return card_dicts

  """ -----------------
      Utility Functions
      ----------------- """

  def get_opponent_positions(self):
    op1 = (self.me - 1) % self.NUM_PLAYERS
    op2 = (self.me + 1) % self.NUM_PLAYERS
    op1_range = [(op1, i) for i in xrange(self.CARDS_PER_PLAYER)]
    op2_range = [(op2, i) for i in xrange(self.CARDS_PER_PLAYER)]
    return op1_range + op2_range

  def is_unclear(self, card):
    return card["rank"] == "Unclear"

  def idx_to_pos(self,idx):
    player = idx / self.CARDS_PER_PLAYER
    card_idx = idx % self.CARDS_PER_PLAYER
    return player, card_idx

  def pos_to_idx(self, player, card_idx):
    return self.CARDS_PER_PLAYER * player + card_idx

  def card_to_num(self,card):
    if self.is_unclear(card):
      return -1 if card["color"] == 1 else -2
    else:
      return card["color"] * self.NUM_RANKS + card["rank"]

  def num_to_card(self, num):
    return {"color": self.num_to_color(num),
            "rank": self.num_to_rank(num)}

  def make_card(self, color, rank):
    return color * self.NUM_RANKS + rank

  def num_to_color(self, num):
    if num < 0:
      return num % 2
    else:
      return num / self.NUM_RANKS

  def num_to_rank(self, num):
    if num < 0:
      return "Unclear"
    return num % self.NUM_RANKS

  def flatten_cards(self, cards):
    flattened = []
    for hand in cards:
      for card in hand:
        flattened.append(card)
    return flattened

  def unflatten_cards(self, cards):
    unflattened = self.empty_array()
    for k in xrange(len(cards)):
      i, j = self.idx_to_pos(k)
      unflattened[i][j] = cards[k]
    return unflattened

  def undict_cards(self, cards):
    new_cards = self.empty_array()
    for i in xrange(self.NUM_PLAYERS):
      for j in xrange(self.CARDS_PER_PLAYER):
        new_cards[i][j] = self.card_to_num(cards[i][j])
    return new_cards

  def extract_colors(self, cards):
    colors = []
    for hand in cards:
      for card in hand:
        colors.append(card["color"])
    return colors

  def empty_array(self):
    return [[None for j in xrange(self.CARDS_PER_PLAYER)] for i in xrange(self.NUM_PLAYERS)]

  def empty_dict(self):
    return [[dict() for j in xrange(self.CARDS_PER_PLAYER)] for i in xrange(self.NUM_PLAYERS)]

  def pprint(self, nested_array):
    """
    Prints a 2-d array in a nicer way.
    """
    for inner_array in nested_array:
      for element in inner_array:
        print element,
      print ""
    print ""

  def pprint_distribution(self, card_dicts):
    for player in card_dicts:
      for card_dict in player:
        print "{",
        for k, v in card_dict.iteritems():
          print "{}: {},".format(k,v),
        print "}"
      print ""
    print ""



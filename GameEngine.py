from Game import Game
from ManualAI import ManualAI
from HannaLarryPlayer import HannaLarryPlayer

num_games = 1000
total_score = [0] * 4
debug = True

for game_count in range(0, num_games):
	AIs = []
	for i in range(4):
 		AIs.append(HannaLarryPlayer(i))
	g = Game(AIs, debug = debug)
	score = [0] * 4
	try:
		score = g.run_game()
	except RuntimeError as e:
		score = e.args[0]
		print(">>> Error: %r <<<" % e.args[1])

	total_score = [sum(x) for x in zip(score, total_score)]
	print("\n\n\n\n\n\n\ngame %d" % game_count)
	print("score is %r" % score)
	print("total score is %r\n\n\n\n\n\n\n" % total_score)
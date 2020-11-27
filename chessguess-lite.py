import sys
from subprocess import call
import chess
import chess.engine
import chess.pgn
import itertools

# arg1:val1 arg2:val2
def parseArguments(args):
    arguments = {}

    for index in range(0, len(args)):
        tupleArgs = args[index].split(":")

        if (len(tupleArgs) == 2):
            arguments[tupleArgs[0]] = tupleArgs[1]

    return arguments

def parseWinner(game):
    if game.headers["Result"] == "1-0":
        return chess.WHITE 
    elif game.headers["Result"] == "0-1":
        return chess.BLACK
    else:
        return None

def main():
    # Start chess engine process (optionally from local install such as: /usr/local/bin/stockfish)
    engine = chess.engine.SimpleEngine.popen_uci("./bin/stockfish")
    engine.configure({"Threads":2, "Hash": 4096})

    pgn = open(scriptArguments["pgn"])
    game = chess.pgn.read_game(pgn)
    board = game.board()
    winner = parseWinner(game)
    cycleNum = 1
    mainLineMoves = []
    for move in game.mainline_moves():
        mainLineMoves.append(move)

    if winner != None:
        for move in mainLineMoves:
            board.push(move)

            if not board.is_game_over(): #and ((winner == chess.WHITE and cycleNum % 2 != 0) or (winner == chess.BLACK and cycleNum % 2 == 0)):
                info = engine.analyse(board, chess.engine.Limit(depth=20), multipv=3)
                comment = ""

                if cycleNum < len(mainLineMoves):
                    print()
                    print(board.fen())
                    print(board.san(mainLineMoves[cycleNum]))

                    for i in range(0, len(info)):
                        if info[i]["score"].relative.score() != None:
                            score = info[i]["score"].relative.score() / 100.0 if info[i]["score"].turn else info[i]["score"].relative.score() / -100.0
                        else:
                            score = "Mate in " + str(info[i]["score"].relative.mate()) if info[i]["score"].turn else "Mate in " + str(info[i]["score"].relative.mate() * -1)
                        
                        firstFiveVariations = itertools.islice(info[i]["pv"], 5)
                        print(board.variation_san(firstFiveVariations) + " (" + str(score) + ")")
                 
            cycleNum += 1

    # Shutdown engine
    engine.quit()

# Globals
scriptArguments = parseArguments(sys.argv)

# Start program
main()

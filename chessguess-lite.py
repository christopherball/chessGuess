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

def printHeader(game):
    print("-----------------------------")
    if game.headers["Event"] != None and game.headers["Event"] != "":
        print((game.headers["Event"][:26] + '...') if len(game.headers["Event"]) > 26 else game.headers["Event"])
    if game.headers["Site"] != None and game.headers["Site"] != "":
        print((game.headers["Site"][:26] + '...') if len(game.headers["Site"]) > 26 else game.headers["Site"])
    if game.headers["Date"] != None and game.headers["Date"] != "":
        print(game.headers["Date"])
    if game.headers["Round"] != None and game.headers["Round"] != "":
        print("Round: " + game.headers["Round"])
    if game.headers["White"] != None and game.headers["White"] != "":
        print("White: " + game.headers["White"])
    if game.headers["Black"] != None and game.headers["Black"] != "":
        print("Black: " + game.headers["Black"])
    if game.headers["Result"] != None and game.headers["Result"] != "":
        print("Result: " + game.headers["Result"])
    if game.headers["ECO"] != None and game.headers["ECO"] != "":
        print("ECO: " + game.headers["ECO"])
    print("-----------------------------")

def getMovePrefix(cycleNum):
    if cycleNum % 2 != 0:
        return str(int(cycleNum / 2 + 0.5)) + "..."
    else:
        return str(int(cycleNum / 2 + 1)) + ". "

def main():
    # Start chess engine process (optionally from local install such as: /usr/local/bin/stockfish)
    engine = chess.engine.SimpleEngine.popen_uci("./bin/stockfish")
    engine.configure({"Threads":2, "Hash": 4096})

    pgn = open(scriptArguments["pgn"])
    game = chess.pgn.read_game(pgn)
    board = game.board()
    winner = parseWinner(game)
    cycleNum = 0
    mainLineMoves = []
    for move in game.mainline_moves():
        mainLineMoves.append(move)

    if winner != None:
        printHeader(game)

        for move in mainLineMoves:
            board.push(move)
            if not board.is_game_over():
                if ((winner == chess.WHITE and cycleNum == 0) or (winner == chess.WHITE and cycleNum % 2 != 0) or (winner == chess.BLACK and cycleNum % 2 == 0)):
                    # If it's whites' first move for a white winner game
                    if (winner == chess.WHITE and cycleNum == 0):
                        print(getMovePrefix(cycleNum) + board.san(board.pop()))
                    # Else If it's whites' turn for a black winner game
                    elif (winner == chess.BLACK and cycleNum % 2 == 0): 
                        if cycleNum > 0:
                            print()
                        print(getMovePrefix(cycleNum) + board.san(board.pop()))
                        board.push(move)

                        if cycleNum < len(mainLineMoves) - 1:
                            print(getMovePrefix(cycleNum + 1) + board.san(mainLineMoves[cycleNum + 1]))
                    # Else If it's blacks' turn for a white winner game
                    elif (winner == chess.WHITE and cycleNum % 2 != 0): 
                        print(getMovePrefix(cycleNum) + board.san(board.pop()))
                        board.push(move)
                        
                        if cycleNum < len(mainLineMoves) - 1:
                            print()
                            print(getMovePrefix(cycleNum + 1) + board.san(mainLineMoves[cycleNum + 1]))

                    # Analyze the board for the next best move
                    info = engine.analyse(board, chess.engine.Limit(depth=22), multipv=3)

                    if cycleNum < len(mainLineMoves):
                        for i in range(0, len(info)):
                            if info[i]["score"].relative.score() != None:
                                score = info[i]["score"].relative.score() / 100.0 if info[i]["score"].turn else info[i]["score"].relative.score() / -100.0
                            else:
                                score = "#" + str(info[i]["score"].relative.mate()) if info[i]["score"].turn else "#" + str(info[i]["score"].relative.mate() * -1)
                            
                            trimmedVariations = itertools.islice(info[i]["pv"], 1) # Increase 1 if you want to show more moves beyond candidate move.
                            print("{:-<12s}> {:<15s}".format(board.variation_san(trimmedVariations) + " ", "(" + str(score) + ")"))
                    
                    if (winner == chess.WHITE and cycleNum == 0):
                        board.push(move)
            
            cycleNum += 1

    # Shutdown engine
    engine.quit()

# Globals
scriptArguments = parseArguments(sys.argv)

# Start program
main()

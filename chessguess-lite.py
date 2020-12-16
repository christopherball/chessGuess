import sys
from subprocess import call
import chess
import chess.engine
import chess.pgn
import itertools
import math

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

def printHeader(game, plyCount, winner):
    print("―――――――――――――――――――――――――――――")
    if game.headers["Event"] != None and game.headers["Event"] != "":
        print((game.headers["Event"][:26] + '...') if len(game.headers["Event"]) > 26 else game.headers["Event"])
    if game.headers["Site"] != None and game.headers["Site"] != "":
        print((game.headers["Site"][:26] + '...') if len(game.headers["Site"]) > 26 else game.headers["Site"])
    if game.headers["Round"] != None and game.headers["Round"] != "":
        print("Round: " + (game.headers["Round"][:19] + '...') if len(game.headers["Round"]) > 19 else "Round: " + game.headers["Round"])
    if game.headers["White"] != None and game.headers["White"] != "":
        print((game.headers["White"][:26] + '...') if len(game.headers["White"]) > 26 else game.headers["White"])
    if game.headers["Black"] != None and game.headers["Black"] != "":
        print((game.headers["Black"][:26] + '...') if len(game.headers["Black"]) > 26 else game.headers["Black"])
    if game.headers["Date"] != None and game.headers["Date"] != "":
        print((game.headers["Date"][:26] + '...') if len(game.headers["Date"]) > 26 else game.headers["Date"])
    if game.headers["Result"] != None and game.headers["Result"] != "":
        print("Result: " + game.headers["Result"])
    if game.headers["ECO"] != None and game.headers["ECO"] != "":
        print("ECO: " + game.headers["ECO"])
    pointsPossible = math.floor((plyCount / 2) - 5) if winner == chess.BLACK else math.ceil((plyCount / 2) - 5)
    print("Total Points Earned:    / " + str(pointsPossible))
    print("―――――――――――――――――――――――――――――")
    print()

def getMovePrefix(cycleNum):
    if cycleNum % 2 != 0:
        return str(int(cycleNum / 2 + 0.5)) + "..."
    else:
        return str(int(cycleNum / 2 + 1)) + ". "

def getPointValues(info, heroMove, board, winner):
    pointDict = {}
    heroScore = None;

    # Taking first pass through engine scorings to compose and extract scores, as well as flag hero score
    for i in range(0, len(info)):
        engineMove = board.san(info[i]["pv"][0])
        score = None
        if info[i]["score"].relative.score() != None:
            score = info[i]["score"].relative.score() / 100.0 if info[i]["score"].turn else info[i]["score"].relative.score() / -100.0
        else:
            score = "#" + str(info[i]["score"].relative.mate()) if info[i]["score"].turn else "#" + str(info[i]["score"].relative.mate() * -1)
            score = (1000 - float(score[1:])) if winner == chess.WHITE else (-1000 - float(score[1:]))
        
        pointDict[i] = { "score": score, "points": 1 if heroMove == engineMove else None, "engineMove": engineMove }
        if heroMove == engineMove:
            heroScore = score

    # This captures the less common scenario where the hero made a move, not considered top 3 choice by the engine.
    if heroScore == None:
        # Locating and matching score of 3rd best move as seed.
        i = len(info)-1
        heroScore = pointDict[i]["score"]

        # Applying appropriate penalty to correlate score with being just outside of top3 scores, based on score scaling.
        if heroScore > 900 or heroScore < -900:
            heroScore = heroScore - 1 if winner == chess.WHITE else heroScore + 1
        else:
            heroScore = heroScore - 0.1 if winner == chess.WHITE else heroScore + 0.1

    # Making second final pass through engine scorings, only using the iterator as a mechanism to backfill missing point assignments in pointDict
    for i in range(0, len(info)):
        if pointDict[i]["points"] == None:
            scoreDiff = heroScore - pointDict[i]["score"]

            if winner == chess.BLACK:
                if scoreDiff <= 0.5 and scoreDiff >= -0.5:
                    pointDict[i]["points"] = 1
                elif scoreDiff > 0.5 and scoreDiff <= 1:
                    pointDict[i]["points"] = 1.5
                elif scoreDiff > 1:
                    pointDict[i]["points"] = 2
                elif scoreDiff < -0.5 and scoreDiff >= -1:
                    pointDict[i]["points"] = 0.5
                elif scoreDiff < -1:
                    pointDict[i]["points"] = 0
            else:
                if scoreDiff <= 0.5 and scoreDiff >= -0.5:
                    pointDict[i]["points"] = 1
                elif scoreDiff > 0.5 and scoreDiff <= 1:
                    pointDict[i]["points"] = 0.5
                elif scoreDiff > 1:
                    pointDict[i]["points"] = 0
                elif scoreDiff < -0.5 and scoreDiff >= -1:
                    pointDict[i]["points"] = 1.5
                elif scoreDiff < -1:
                    pointDict[i]["points"] = 2
    return pointDict

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
        printHeader(game, len(mainLineMoves), winner)

        for move in mainLineMoves:
            board.push(move)
            if not board.is_game_over():
                if ((winner == chess.WHITE and cycleNum == 0) or (winner == chess.WHITE and cycleNum % 2 != 0) or (winner == chess.BLACK and cycleNum % 2 == 0)):
                    # If it's whites' first move for a white winner game
                    if (winner == chess.WHITE and cycleNum == 0):
                        print(getMovePrefix(cycleNum) + " " + board.san(board.pop()))
                    # Else If it's whites' turn for a black winner game
                    elif (winner == chess.BLACK and cycleNum % 2 == 0): 
                        if cycleNum > 0:
                            print()
                            if cycleNum % 5 == 0:
                                board.pop()
                                print("|" + board.fen())
                                print()
                                board.push(move)
                        print(getMovePrefix(cycleNum) + " " + board.san(board.pop()))
                        board.push(move)

                        if cycleNum < len(mainLineMoves) - 1:
                            print(getMovePrefix(cycleNum + 1) + board.san(mainLineMoves[cycleNum + 1]))
                    # Else If it's blacks' turn for a white winner game
                    elif (winner == chess.WHITE and cycleNum % 2 != 0): 
                        print(getMovePrefix(cycleNum) + board.san(board.pop()))
                        board.push(move)
                        
                        if cycleNum < len(mainLineMoves) - 1:
                            print()
                            if (cycleNum + 1) % 5 == 0:
                                print("|" + board.fen())
                                print()
                            print(getMovePrefix(cycleNum + 1) + " " + board.san(mainLineMoves[cycleNum + 1]))
                    # If we are past the opening cycleNum plys, it's time to start analyzing top 3 moves from here onward
                    if (cycleNum > 8 and winner == chess.WHITE) or (cycleNum > 9 and winner == chess.BLACK):
                        # Analyze the board for the next best move
                        info = engine.analyse(board, chess.engine.Limit(depth=22), multipv=3)

                        if cycleNum < len(mainLineMoves):
                            pointDict = getPointValues(info, board.san(mainLineMoves[cycleNum + 1]), board, winner)
                            for i in range(0, len(info)):
                                if info[i]["score"].relative.score() != None:
                                    score = info[i]["score"].relative.score() / 100.0 if info[i]["score"].turn else info[i]["score"].relative.score() / -100.0
                                else:
                                    score = "#" + str(info[i]["score"].relative.mate()) if info[i]["score"].turn else "#" + str(info[i]["score"].relative.mate() * -1)
                                
                                trimmedVariations = itertools.islice(info[i]["pv"], 1) # Increase 1 if you want to show more moves beyond candidate move.
                                move = board.variation_san(trimmedVariations) if cycleNum % 2 == 0 else board.variation_san(trimmedVariations).replace(" ","  ")
                                print("{:―<12s}▸ {:<9s} {:<5s}".format(move + " ", "(" + str(score) + ")", "[" + str(pointDict[i]["points"]) + "]"))
                    
                    if (winner == chess.WHITE and cycleNum == 0):
                        board.push(move)
            cycleNum += 1
        print()
    # Shutdown engine
    engine.quit()

# Globals
scriptArguments = parseArguments(sys.argv)

# Start program
main()

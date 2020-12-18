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

def queuePrint(str):
    printQueue.append(str)

def printHeader(game):
    queuePrint("―――――――――――――――――――――――――――――")
    if game.headers["Event"] != None and game.headers["Event"] != "":
        queuePrint((game.headers["Event"][:26] + '...') if len(game.headers["Event"]) > 26 else game.headers["Event"])
    if game.headers["Site"] != None and game.headers["Site"] != "":
        queuePrint((game.headers["Site"][:26] + '...') if len(game.headers["Site"]) > 26 else game.headers["Site"])
    if game.headers["Round"] != None and game.headers["Round"] != "":
        queuePrint("Round: " + (game.headers["Round"][:19] + '...') if len(game.headers["Round"]) > 19 else "Round: " + game.headers["Round"])
    if game.headers["White"] != None and game.headers["White"] != "":
        queuePrint(("W: " + game.headers["White"][:23] + '...') if len(game.headers["White"]) > 23 else ("W: " + game.headers["White"]))
    if game.headers["Black"] != None and game.headers["Black"] != "":
        queuePrint(("B: " + game.headers["Black"][:23] + '...') if len(game.headers["Black"]) > 23 else ("B: " + game.headers["Black"]))
    if game.headers["Date"] != None and game.headers["Date"] != "":
        queuePrint(("Date: " + game.headers["Date"][:20] + '...') if len(game.headers["Date"]) > 20 else ("Date: " + game.headers["Date"]))
    if game.headers["Result"] != None and game.headers["Result"] != "":
        queuePrint("Result: " + game.headers["Result"])
    if game.headers["ECO"] != None and game.headers["ECO"] != "":
        queuePrint("ECO: " + game.headers["ECO"])
    
    queuePrint("Winner Points: totalHeroPoints")
    queuePrint("Your Points: ")
    queuePrint("―――――――――――――――――――――――――――――")
    queuePrint("")

def getMovePrefix(cycleNum):
    if cycleNum % 2 != 0:
        return str(int(cycleNum / 2 + 0.5)) + "..."
    else:
        return str(int(cycleNum / 2 + 1)) + ". "

def getPointValues(info, heroMove, board, winner):
    pointDict = {}

    # Taking first pass through engine scorings to compose and extract scores
    for i in range(0, len(info)):
        engineMove = board.san(info[i]["pv"][0])
        score = None
        if info[i]["score"].relative.score() != None:
            score = info[i]["score"].relative.score() / 100.0 if info[i]["score"].turn else info[i]["score"].relative.score() / -100.0
        else:
            score = "#" + str(info[i]["score"].relative.mate()) if info[i]["score"].turn else "#" + str(info[i]["score"].relative.mate() * -1)
            score = (1000 - float(score[1:])) if winner == chess.WHITE else (-1000 - float(score[1:]))
        
        pointDict[i] = { "score": score, "points": None, "engineMove": engineMove }

    # Making second pass through engine scorings, only using the iterator as a mechanism to backfill missing point assignments in pointDict
    for i in range(0, len(info)):
        if pointDict[i]["points"] == None:
            if i == 0:
                pointDict[i]["points"] = 3
            else:
                scoreDiff = pointDict[0]["score"] - pointDict[i]["score"]
                if winner == chess.BLACK:
                    if scoreDiff >= -0.25:
                        pointDict[i]["points"] = 3
                    elif scoreDiff >= -0.75:
                        pointDict[i]["points"] = 2
                    elif scoreDiff >= -1.25:
                        pointDict[i]["points"] = 1
                    else:
                        pointDict[i]["points"] = 0
                else:
                    if scoreDiff <= 0.25:
                        pointDict[i]["points"] = 3
                    elif scoreDiff <= 0.75:
                        pointDict[i]["points"] = 2
                    elif scoreDiff <= 1.25:
                        pointDict[i]["points"] = 1
                    else:
                        pointDict[i]["points"] = 0
    
    # Making third and final pass through engine scorings, with the sole purpose of updating our global tally of how the hero performed
    global totalHeroPoints 
    for i in range(0, len(info)):
        if pointDict[i]["engineMove"] == heroMove:
            totalHeroPoints += pointDict[i]["points"]

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
        printHeader(game)

        for move in mainLineMoves:
            board.push(move)
            if not board.is_game_over():
                if ((winner == chess.WHITE and cycleNum == 0) or (winner == chess.WHITE and cycleNum % 2 != 0) or (winner == chess.BLACK and cycleNum % 2 == 0)):
                    # If it's whites' first move for a white winner game
                    if (winner == chess.WHITE and cycleNum == 0):
                        queuePrint(getMovePrefix(cycleNum) + " " + board.san(board.pop()))
                    # Else If it's whites' turn for a black winner game
                    elif (winner == chess.BLACK and cycleNum % 2 == 0): 
                        if cycleNum > 0:
                            queuePrint("")
                            if cycleNum % 5 == 0:
                                board.pop()
                                queuePrint("|" + board.fen())
                                queuePrint("")
                                board.push(move)
                        queuePrint(getMovePrefix(cycleNum) + " " + board.san(board.pop()))
                        board.push(move)

                        if cycleNum < len(mainLineMoves) - 1:
                            queuePrint(getMovePrefix(cycleNum + 1) + board.san(mainLineMoves[cycleNum + 1]))
                    # Else If it's blacks' turn for a white winner game
                    elif (winner == chess.WHITE and cycleNum % 2 != 0): 
                        queuePrint(getMovePrefix(cycleNum) + board.san(board.pop()))
                        board.push(move)
                        
                        if cycleNum < len(mainLineMoves) - 1:
                            queuePrint("")
                            if (cycleNum + 1) % 5 == 0:
                                queuePrint("|" + board.fen())
                                queuePrint("")
                            queuePrint(getMovePrefix(cycleNum + 1) + " " + board.san(mainLineMoves[cycleNum + 1]))
                    # If we are past the opening cycleNum plys, it's time to start analyzing top 3 moves from here onward
                    if (cycleNum > 8 and winner == chess.WHITE) or (cycleNum > 9 and winner == chess.BLACK):
                        # Analyze the board for the next best move
                        info = engine.analyse(board, chess.engine.Limit(depth=24), multipv=3)

                        if cycleNum < len(mainLineMoves):
                            pointDict = getPointValues(info, board.san(mainLineMoves[cycleNum + 1]), board, winner)
                            for i in range(0, len(info)):
                                if info[i]["score"].relative.score() != None:
                                    score = info[i]["score"].relative.score() / 100.0 if info[i]["score"].turn else info[i]["score"].relative.score() / -100.0
                                else:
                                    score = "#" + str(info[i]["score"].relative.mate()) if info[i]["score"].turn else "#" + str(info[i]["score"].relative.mate() * -1)
                                
                                trimmedVariations = itertools.islice(info[i]["pv"], 1) # Increase 1 if you want to show more moves beyond candidate move.
                                move = board.variation_san(trimmedVariations) if cycleNum % 2 == 0 else board.variation_san(trimmedVariations).replace(" ","  ")
                                queuePrint("{:―<12s}▸ {:<9s} {:<5s}".format(move + " ", "(" + str(score) + ")", "[" + str(pointDict[i]["points"]) + "]"))
                    
                    if (winner == chess.WHITE and cycleNum == 0):
                        board.push(move)
            cycleNum += 1
        queuePrint("")
    # Shutdown engine
    engine.quit()

    # Update printQueue with totalHeroPoints and then print results
    for i in range(0, len(printQueue)):
        if "totalHeroPoints" in printQueue[i]:
            printQueue[i] = printQueue[i].replace("totalHeroPoints", str(totalHeroPoints))

        print(printQueue[i])

# Globals
scriptArguments = parseArguments(sys.argv)
printQueue = []
totalHeroPoints = 0

# Start program
main()

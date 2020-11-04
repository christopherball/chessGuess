import sys
from subprocess import call
import chess
import chess.engine
import chess.pgn
import re
from io import StringIO
import csv
from string import digits

def readFileToString(fileName):
    with open(fileName, 'r') as myFile:
        return myFile.read()

def getMinimalPGNString(fileContents):
    trimmedFileString = re.sub('\[.*\]', '', fileContents)
    trimmedFileString = re.sub('\{.*\}', '', trimmedFileString)
    trimmedFileString = trimmedFileString.replace('\n', ' ')
    trimmedFileString = re.sub('\s+', ' ', trimmedFileString).strip()
    return trimmedFileString

def rewindAndSubstitute(minPGNString, moveNum, move, playAs):
    if (playAs == 'White'):
        minPGNString = re.sub(str(moveNum) + '\..+', str(moveNum) + '. ', minPGNString)
    else:
        minPGNString = re.match('.*( )' + str(moveNum) + '\.( )[^ ]+( )', minPGNString).group()

    minPGNString += move
    return minPGNString

# arg1:val1 arg2:val2
def parseArguments(args):
    arguments = {}

    for index in range(0, len(args)):
        tupleArgs = args[index].split(":")

        if (len(tupleArgs) == 2):
            arguments[tupleArgs[0]] = tupleArgs[1]

    return arguments

def getOutputFileName(filePath):
    trimmed = re.sub(".*\/", "", filePath)
    trimmed = re.sub("\..*", "", trimmed)
    return trimmed + ".csv"

# Setup chess board
def setupBoard(game, targetMoveNum, playAs, pushAll):
    board = game.board()

    #Path only walked for guess move analysis since PGN is gradually built up each stage
    if (pushAll):
        for move in game.mainline_moves():
            board.push(move)

        return board

    currentMoveNum = 1

    # Current move is for white
    isHalfMove = False

    for move in game.mainline_moves():
        if ((currentMoveNum < targetMoveNum) or (currentMoveNum == targetMoveNum and playAs == 'Black' and isHalfMove == False)):
            board.push(move)

            if (isHalfMove):
                currentMoveNum += 1
                isHalfMove = False
            else:
                isHalfMove = True
        else:
            break

    return board

# Read all lines from a given file into an in-memory list
def readLines(filePath):
    lines = []
    with open(filePath, "r") as f:
        for line in f:
            lines.append(line.rstrip('\n'))

    return lines

def loadMoves(game):
    moves = []
    for i in game.main_line():
        moves.append(i)

    return moves

# Returns the string color of the player currently playing on the board.
def getTurnColor(board):
    return 'White' if board.turn else 'Black'

# Determines whether endgame state has been reached.
def isEndgame(fen):
    fenLite = fen.split(" ")[0].replace("/","").replace("p","").replace("P","").replace("k","").replace("K","")
    removeDigits = str.maketrans('', '', digits)
    fenLiter = fenLite.translate(removeDigits)
    bScore = 0
    wScore = 0

    for i in fenLiter:
        if i == 'Q':
            wScore += 9
        elif i == 'R':
            wScore += 5
        elif i == 'B' or i == 'N':
            wScore += 3
        elif i == 'q':
            bScore += 9
        elif i == 'r':
            bScore += 5
        elif i == 'b' or i == 'n':
            bScore += 3

    return True if wScore <= 6 and bScore <= 6 else False

# Used to generate a single record of analysis (one record per guess, actual, or best - combined later in process).
def generateRecordResult(engine, game, currentMoveNum, playAs, recordType, currentGuessMove):
    # Tell engine the current position of the board and display it
    board = setupBoard(game, currentMoveNum, playAs, True if recordType == 'Guess' else False)

    # Generating our full record set
    record = {}
    record['DatePlayed'] = guessArguments['datePlayed']
    record['PlayAs'] = guessArguments['playAs']
    scoreDivider = 100.0 if playAs == 'White' else -100.0
    scoreMultiplier = 1 if playAs == 'White' else -1
    depth = 22 if isEndgame(board.fen()) == False else 30
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    scoreObj = info["score"].white() if playAs == 'White' else info["score"].black()
    
    if (recordType == "Guess"):
        record['MoveNum'] = currentMoveNum
        record['PostGuessBoardFEN'] = board.fen()
        record['GuessScore'] = scoreObj.score() / scoreDivider if info["score"].is_mate() == False else ""
        record['GuessMove'] = currentGuessMove
        record['GuessMate'] = scoreObj.mate() * scoreMultiplier if info["score"].is_mate() == True else ""

    if (recordType == "Actual"):
        record['GameIdentifier'] = scriptArguments["pgn"]
        record['PostActualBoardFEN'] = board.fen()
        record['ActualScore'] = scoreObj.score() / scoreDivider if info["score"].is_mate() == False else ""
        record['ActualMove'] = board.san(board.pop())
        record['ActualMate'] = scoreObj.mate() * scoreMultiplier if info["score"].is_mate() == True else ""

    if (recordType == "Best"):
        record['PreGuessBoardFEN'] = board.fen()
        record['BestScore'] = scoreObj.score() / scoreDivider if info["score"].is_mate() == False else ""
        record['BestMove'] = str(board.san(info["pv"][0]))
        record['BestMate'] = (scoreObj.mate() - 1) * scoreMultiplier if info["score"].is_mate() == True else ""

    return record

def generateCSVOutput(dictionaries, fileName):
    with open(fileName, 'w', newline='') as f:
        fieldNames = [
            'DatePlayed',
            'GameIdentifier',
            'PlayAs',
            'MoveNum',
            'GuessMove',
            'ActualMove',
            'BestMove', 
            'GuessScore',
            'ActualScore',
            'BestScore', 
            'GuessMate',
            'ActualMate',
            'BestMate', 
            'PreGuessBoardFEN', 
            'PostGuessBoardFEN',
            'PostActualBoardFEN']
        writer = csv.DictWriter(f, fieldnames=fieldNames)
        writer.writeheader()
        writer.writerows(dictionaries)

# For times where the guessMove matched actualMove, or actualMove matched bestMove, or guessMove matched bestMove, scores should match
def alignScores(bestDict, guessDict, actualDict):
    if (bestDict['BestMove'] == guessDict['GuessMove'] and bestDict['BestMove'] == actualDict['ActualMove'] and bestDict['BestScore'] != ''):
        avgScore = round((bestDict['BestScore'] + guessDict['GuessScore'] + actualDict['ActualScore']) / 3, 2)
        bestDict['BestScore'] = avgScore
        guessDict['GuessScore'] = avgScore
        actualDict['ActualScore'] = avgScore
    if (bestDict['BestMove'] == guessDict['GuessMove'] and bestDict['BestScore'] != ''):
        avgScore = round((bestDict['BestScore'] + guessDict['GuessScore']) / 2, 2)
        bestDict['BestScore'] = avgScore
        guessDict['GuessScore'] = avgScore
    if (bestDict['BestMove'] == actualDict['ActualMove'] and bestDict['BestScore'] != ''):
        avgScore = round((bestDict['BestScore'] + actualDict['ActualScore']) / 2, 2)
        bestDict['BestScore'] = avgScore
        actualDict['ActualScore'] = avgScore
    if (guessDict['GuessMove'] == actualDict['ActualMove'] and guessDict['GuessScore'] != ''):
        avgScore = round((guessDict['GuessScore'] + actualDict['ActualScore']) / 2, 2)
        guessDict['GuessScore'] = avgScore
        actualDict['ActualScore'] = avgScore

    return {**bestDict, **guessDict, **actualDict}

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

# Entry point method
def main():
    # Start chess engine process
    engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")

    # Initialize specified engine
    engine.configure({"Threads":2, "Hash": 4096})

    # Generate analysis records
    finalResultRecordDicts = []
    startingMove = int(guessArguments["startingMove"])
    finalMove = startingMove + len(guessLines) - 2
    guessIndex = 1
    printProgressBar(0, finalMove - startingMove, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    for currentMoveNum in range(startingMove, startingMove + len(guessLines) - 1):
        game = chess.pgn.read_game(StringIO(minPGNString))
        resultDict1 = generateRecordResult(engine, game, currentMoveNum, guessArguments["playAs"], "Best", "")

        rewoundMinPGNString = rewindAndSubstitute(minPGNString, currentMoveNum, guessLines[guessIndex], guessArguments["playAs"])
        game = chess.pgn.read_game(StringIO(rewoundMinPGNString))
        resultDict2 = generateRecordResult(engine, game, currentMoveNum, guessArguments["playAs"], "Guess", guessLines[guessIndex])
        guessIndex += 1

        game = chess.pgn.read_game(StringIO(minPGNString))
        resultDict3 = generateRecordResult(engine, game, currentMoveNum if guessArguments["playAs"] == 'White' else currentMoveNum + 1, 'Black' if guessArguments["playAs"] == 'White' else 'White', "Actual", "")
       
        combinedResultDict = alignScores(resultDict1, resultDict2, resultDict3)
        finalResultRecordDicts.append(combinedResultDict)
        printProgressBar(currentMoveNum - startingMove, finalMove - startingMove, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Generate csv output for external analysis
    fileName = getOutputFileName(scriptArguments["pgn"])
    generateCSVOutput(finalResultRecordDicts, "./output/" + fileName)

    engine.quit()

# Globals
scriptArguments = parseArguments(sys.argv)
fileString = readFileToString(scriptArguments["pgn"])
minPGNString = getMinimalPGNString(fileString)
guessLines = readLines(scriptArguments["guess"])
guessArguments = parseArguments(guessLines[0].split())

# Start program
main()

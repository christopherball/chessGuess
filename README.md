This program is designed for very custom self-study chess needs from books and other resources.  The goal of this program is to automatically analyze real chess games of high-level play, comparing your guesses, from the perspective of the winner, at each step of the way (starting after the opening), producing a CSV output for further analysis and charting.  
For example purposes, this code base includes the first 5 games (in pgn format) from the book "Logical Chess Move By Move" by Chernev, alongside 5 example "guess" files signaling the formatting requirements.  Upon execution, results are generated in the `./output` folder.

**Dependencies (Required):**  
`python3 -m pip install --force-reinstall chess`  

**Dependencies (Optional):**  
Stockfish 12 has been bundled with the code, but can be referenced locally if preferred.  For MAC users, one can install the latest stockfish binaries via:  
`brew install stockfish`  

**Example commands:**  
(Verbose)  
`python3 chessguess.py pgn:pgn/logical_chess_game_1.pgn guess:guess/logical_chess_game_1.guess`

(Short-cut)  
`./analyze logical_chess_game_1`  

**Output:**  
Results in a CSV summary report comparing your move, to the hero, to the engine choice...  

|DatePlayed|GameIdentifier              |PlayAs|MoveNum|GuessMove|ActualMove|BestMove|GuessScore|ActualScore|BestScore|GuessMate|ActualMate|BestMate|PreGuessBoardFEN                                                      |PostGuessBoardFEN                                                     |PostActualBoardFEN                                                    |
|----------|----------------------------|------|-------|---------|----------|--------|----------|-----------|---------|---------|----------|--------|----------------------------------------------------------------------|----------------------------------------------------------------------|----------------------------------------------------------------------|
|12/28/17  |pgn/logical_chess_game_5.pgn|White |10     |Qd4      |Qc2       |Qc2     |0.79      |2.17       |2.17     |         |          |        |r1bq1rk1/ppppnppp/8/3PP3/1bB1n3/2N2N2/PP3PPP/R1BQK2R w KQ - 1 10      |r1bq1rk1/ppppnppp/8/3PP3/1bBQn3/2N2N2/PP3PPP/R1B1K2R b KQ - 2 10      |r1bq1rk1/ppppnppp/8/3PP3/1bB1n3/2N2N2/PPQ2PPP/R1B1K2R b KQ - 2 10     |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |11     |bxc3     |bxc3      |bxc3    |2.18      |2.18       |2.18     |         |          |        |r1bq1rk1/ppppnppp/8/3PP3/1bB5/2n2N2/PPQ2PPP/R1B1K2R w KQ - 0 11       |r1bq1rk1/ppppnppp/8/3PP3/1bB5/2P2N2/P1Q2PPP/R1B1K2R b KQ - 0 11       |r1bq1rk1/ppppnppp/8/3PP3/1bB5/2P2N2/P1Q2PPP/R1B1K2R b KQ - 0 11       |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |12     |Ng5      |Ng5       |Ng5     |3.22      |3.22       |3.22     |         |          |        |r1bq1rk1/ppppnppp/8/2bPP3/2B5/2P2N2/P1Q2PPP/R1B1K2R w KQ - 1 12       |r1bq1rk1/ppppnppp/8/2bPP1N1/2B5/2P5/P1Q2PPP/R1B1K2R b KQ - 2 12       |r1bq1rk1/ppppnppp/8/2bPP1N1/2B5/2P5/P1Q2PPP/R1B1K2R b KQ - 2 12       |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |13     |e6       |h4        |h4      |-0.89     |3.38       |3.38     |         |          |        |r1bq1rk1/pppp1ppp/6n1/2bPP1N1/2B5/2P5/P1Q2PPP/R1B1K2R w KQ - 3 13     |r1bq1rk1/pppp1ppp/4P1n1/2bP2N1/2B5/2P5/P1Q2PPP/R1B1K2R b KQ - 0 13    |r1bq1rk1/pppp1ppp/6n1/2bPP1N1/2B4P/2P5/P1Q2PP1/R1B1K2R b KQ - 0 13    |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |14     |h5       |d6        |d6      |5.09      |9.23       |9.23     |         |          |        |r1bq1rk1/pppp1pp1/6np/2bPP1N1/2B4P/2P5/P1Q2PP1/R1B1K2R w KQ - 0 14    |r1bq1rk1/pppp1pp1/6np/2bPP1NP/2B5/2P5/P1Q2PP1/R1B1K2R b KQ - 0 14     |r1bq1rk1/pppp1pp1/3P2np/2b1P1N1/2B4P/2P5/P1Q2PP1/R1B1K2R b KQ - 0 14  |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |15     |Qxg6     |hxg5      |Qxg6    |          |           |         |6        |6         |6       |r1bq1rk1/pppp1pp1/3P2n1/2b1P1p1/2B4P/2P5/P1Q2PP1/R1B1K2R w KQ - 0 15  |r1bq1rk1/pppp1pp1/3P2Q1/2b1P1p1/2B4P/2P5/P4PP1/R1B1K2R b KQ - 0 15    |r1bq1rk1/pppp1pp1/3P2n1/2b1P1P1/2B5/2P5/P1Q2PP1/R1B1K2R b KQ - 0 15   |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |16     |Qxg6     |Qxg6      |Qxg6    |          |           |         |4        |4         |4       |r1bqr1k1/pppp1pp1/3P2n1/2b1P1P1/2B5/2P5/P1Q2PP1/R1B1K2R w KQ - 1 16   |r1bqr1k1/pppp1pp1/3P2Q1/2b1P1P1/2B5/2P5/P4PP1/R1B1K2R b KQ - 0 16     |r1bqr1k1/pppp1pp1/3P2Q1/2b1P1P1/2B5/2P5/P4PP1/R1B1K2R b KQ - 0 16     |
|12/28/17  |pgn/logical_chess_game_5.pgn|White |17     |Kf1      |Kf1       |Be3     |          |           |         |10       |10        |3       |r1bq2k1/pppp1pp1/3P2Q1/2b1r1P1/2B5/2P5/P4PP1/R1B1K2R w KQ - 0 17      |r1bq2k1/pppp1pp1/3P2Q1/2b1r1P1/2B5/2P5/P4PP1/R1B2K1R b - - 1 17       |r1bq2k1/pppp1pp1/3P2Q1/2b1r1P1/2B5/2P5/P4PP1/R1B2K1R b - - 1 17       |


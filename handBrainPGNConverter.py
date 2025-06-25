import chess.pgn
import sys

PIECE_MAP = {
    chess.PAWN: "pawn",
    chess.KNIGHT: "knight",
    chess.BISHOP: "bishop",
    chess.ROOK: "rook",
    chess.QUEEN: "queen",
    chess.KING: "king"
}

def get_piece_type(move, board):
    if board.is_castling(move):
        return "king"
    piece = board.piece_at(move.from_square)
    if piece:
        return PIECE_MAP[piece.piece_type]
    else:
        return "unknown"

def process_game(filename, color):
    color = color.lower()
    if color not in ["white", "black"]:
        raise ValueError("Color must be 'white' or 'black'")

    with open(filename, 'r') as pgn:
        game = chess.pgn.read_game(pgn)

    if game is None:
        raise ValueError("No game found in PGN file.")

    board = game.board()

    output_lines = []
    move_number = 1

    moves = list(game.mainline_moves())
    i = 0

    # Determine the width needed for the largest move number
    max_move_number = (len(moves) + 1) // 2
    move_number_width = len(str(max_move_number))

    while i < len(moves):
        # Move prefix like "1." with correct padding
        prefix = f"{move_number}.".ljust(move_number_width + 2)

        # White's move
        move = moves[i]
        is_guessing = color == "white"

        if is_guessing:
            piece_type = get_piece_type(move, board)
            white_part = f"{piece_type:<8}"
        else:
            white_part = f"{board.san(move):<8}"

        board.push(move)
        i += 1

        # Black's move (if exists)
        if i < len(moves):
            move = moves[i]
            is_guessing = color == "black"

            if is_guessing:
                piece_type = get_piece_type(move, board)
                black_part = f"{piece_type:<8}"
            else:
                black_part = f"{board.san(move):<8}"

            board.push(move)
            i += 1
        else:
            black_part = ""

        line = f"{prefix}{white_part} {black_part}".rstrip()
        output_lines.append(line)

        move_number += 1

    return "\n".join(output_lines)


# ==== Usage Example ====
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python hand_and_brain_pgn.py filename.pgn color")
        sys.exit(1)

    filename = sys.argv[1]
    color = sys.argv[2]

    try:
        output = process_game(filename, color)
        print(output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


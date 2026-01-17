from pieces import Bishop, King, Knight, Pawn, Queen, Rook


def map_piece_to_fullname(piece):
    if piece is None:
        return "<empty>"

    c = None
    if isinstance(piece, Pawn):
        c = "Pawn"
    if isinstance(piece, Rook):
        c = "Rook"
    if isinstance(piece, Knight):
        c = "Knight"
    if isinstance(piece, Bishop):
        c = "Bishop"
    if isinstance(piece, Queen):
        c = "Queen"
    if isinstance(piece, King):
        c = "King"

    return c


def map_piece_to_character(piece):
    if piece is None:
        return "."

    c = None
    if isinstance(piece, Pawn):
        c = "P"
    if isinstance(piece, Rook):
        c = "R"
    if isinstance(piece, Knight):
        c = "N"
    if isinstance(piece, Bishop):
        c = "B"
    if isinstance(piece, Queen):
        c = "Q"
    if isinstance(piece, King):
        c = "K"

    if piece.is_white():
        return c

    return c.lower()


def cell_to_string(cell):
    files = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return files[cell[1]] + str(cell[0] + 1)


class InvalidRowException(Exception):
    def __init__(self, cell):
        self.cell = cell


class InvalidColumnException(Exception):
    def __init__(self, cell):
        self.cell = cell

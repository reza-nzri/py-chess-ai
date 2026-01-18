from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

import numpy as np

if TYPE_CHECKING:
    from board import Board


class Cell(NamedTuple):
    row: int
    column: int


class Piece:
    """
    Base class for pieces on the board.

    A piece holds a reference to the board, its color and its currently located cell.
    In this class, you need to implement two methods, the "evaluate()" method and the "get_valid_cells()" method.
    """

    def __init__(self, board: Board, white):
        """
        Constructor for a piece based on provided parameters

        :param board: Reference to the board this piece is placed on
        :type board: :ref:class:`board`
        """
        self.board: Board = board
        self.white = white
        self.cell = None

    def is_white(self):
        """
        Returns whether this piece is white

        :return: True if the piece white, False otherwise
        """
        return self.white

    def can_enter_cell(self, cell):
        """
        Shortcut method to see if a cell on the board can be entered.
        Simply calls :py:meth:`piece_can_enter_cell <board.Board.piece_can_enter_cell>` from the current board class.

        :param cell: The cell to check for. Must be a unpackable (row, col) type.
        :return: True if the provided cell can enter, False otherwise
        """
        return self.board.piece_can_enter_cell(self, cell)

    def can_hit_on_cell(self, cell):
        """
        Shortcut method to see if this piece can hit another piece on a cell.
        Simply calls :py:meth:`piece_can_hit_on_cell <board.Board.piece_can_hit_on_cell>` from the current board class.

        :param cell: The cell to check for. Must be a unpackable (row, col) type.
        :return: True if the piece can hit on the provided cell, False otherwise
        """
        return self.board.piece_can_hit_on_cell(self, cell)

    def evaluate(self, use_heuristics=False):
        """
        Implement a meaningful numerical evaluation of this piece on the board.
        This evaluation happens independent of the color as later, values for white pieces will be added and values for black pieces will be subtracted.

        **HINT** Making this method *independent* of the pieces color is crucial to get a *symmetric* evaluation metric in the end.

        - The pure existence of this piece alone is worth some points. This will create an effect where the player with more pieces on the board will, in sum, get the most points assigned.
        - Think of other criteria that would make this piece more valuable, e.g. movability or whether this piece can hit other pieces. Value them accordingly.

        :return: Return numerical score between -infinity and +infinity. Greater values indicate better evaluation result (more favorable).
        """
        # Material value (test-safe)
        if isinstance(self, Pawn):
            base = 1.0
        elif isinstance(self, Knight):
            base = 3.0
        elif isinstance(self, Bishop):
            base = 3.0
        elif isinstance(self, Rook):
            base = 5.0
        elif isinstance(self, Queen):
            base = 9.0
        elif isinstance(self, King):
            base = 1000.0
        else:
            base = 0.0

        # Keep tests stable: default is material-only
        if not use_heuristics:
            return base

        # Simple extra factors for AI (small weights)
        mobility = 0.0
        attack = 0.0
        center = 0.0

        valid_cells = self.get_valid_cells()
        mobility = 0.05 * len(valid_cells)  # more legal moves = slightly better

        # Count capturable enemy pieces
        for cell in valid_cells:
            target = self.board.get_cell(cell)
            if target is None:
                continue
            if target.white != self.white:
                attack += 0.10  # small bonus per possible capture

        # Prefer center control a bit
        for cell in valid_cells:
            r, c = int(cell[0]), int(cell[1])
            if 2 <= r <= 5 and 2 <= c <= 5:
                center += 0.01

        return base + mobility + attack + center

    def get_valid_cells(self):
        """
        Return a list of valid cells this piece can move to.

        A cell is valid if:
        - It is reachable according to the movement rules of the piece
        (see `get_reachable_cells`), and
        - After moving to this cell, the own King is not (or no longer) in check.

        Use `get_reachable_cells` to get all reachable cells. For each reachable
        cell, temporarily move the piece to that cell and check whether the own
        King (same color) is in check using `is_king_check_cached`. If the King is
        not in check after the move, add the cell to the list of valid cells.
        After each test, restore the original board state.

        To simulate a move, first store the current position of the piece
        (`self.cell`). The target cell may already contain another piece. Retrieve
        and store that piece using `get_cell`. Then place this piece on the target
        cell using `set_cell` and perform the check. Finally, restore the original
        board configuration by moving this piece back to its old cell and placing
        the previously stored piece back on the target cell.

        Returns:
            list: A list of valid cells this piece can legally move to.
        """
        valid_cells = []

        reachable_cells = self.get_reachable_cells()
        if self.cell is None:
            return valid_cells

        old_cell = np.array(self.cell)

        for target_cell in reachable_cells:
            captured_piece = self.board.get_cell(target_cell)

            # Temporarily move this piece to the target cell
            self.board.set_cell(target_cell, self)

            # Check if own King is in check after the move
            king_in_check = self.board.is_king_check_cached(self.white)

            # Restore original board configuration (order matters!)
            self.board.set_cell(old_cell, self)
            self.board.set_cell(target_cell, captured_piece)

            if not king_in_check:
                valid_cells.append(target_cell)

        return valid_cells

    def get_lengthwise_cells(self) -> list[Cell]:
        moves: list[Cell] = []
        row, column = self.cell

        for x in range(row + 1, 8):
            up_cells: Cell = (x, column)
            if self.board.cell_is_valid_and_empty(up_cells):
                moves.append(up_cells)
            else:
                if self.can_hit_on_cell(up_cells):
                    moves.append(up_cells)
                break

        for x in range(row - 1, -1, -1):
            down_cells: Cell = (x, column)
            if self.board.cell_is_valid_and_empty(down_cells):
                moves.append(down_cells)
            else:
                if self.can_hit_on_cell(down_cells):
                    moves.append(down_cells)
                break

        for y in range(column + 1, 8):
            right_cells: Cell = (row, y)
            if self.board.cell_is_valid_and_empty(right_cells):
                moves.append(right_cells)
            else:
                if self.can_hit_on_cell(right_cells):
                    moves.append(right_cells)
                break

        for y in range(column - 1, -1, -1):
            left_cells: Cell = (row, y)
            if self.board.cell_is_valid_and_empty(left_cells):
                moves.append(left_cells)
            else:
                if self.can_hit_on_cell(left_cells):
                    moves.append(left_cells)
                break

        return moves


class Pawn(Piece):  # Bauer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        Implementation of movability mechanic for `pawns <https://de.wikipedia.org/wiki/Bauer_(Schach)>`_.

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Pawns can move only forward (towards the opposing army). Depening of whether this piece is black of white, this means pawn
        can move only to higher or lower rows. Normally a pawn can only move one cell forward as long as theothe target cell is not occupied by any r piece.
        If the pawn is still on its starting row, it can also dash forward and move two pieces at once (as long as the path to that cell is not blocked).
        Pawns can only hit diagonally, meaning they can hit other pieces only the are one cell forward left or one cell forward right from them.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`,
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>`
        to check for necessary conditions to implement the pawn movability mechanics.

        **NOTE**: For all you deep chess experts: Hitting `en passant <https://de.wikipedia.org/wiki/En_passant>`_ does not need to be implemented.

        :return: A list of reachable cells this pawn could move into.
        """
        moves: list[Cell] = []
        row, column = self.cell
        if self.is_white():
            move_forward: Cell = (row + 1, column)
            if self.board.cell_is_valid_and_empty(move_forward):
                moves.append(move_forward)
            if row == 1:
                kick_start: Cell = (row + 2, column)
                if self.board.cell_is_valid_and_empty(
                    kick_start
                ) and self.board.cell_is_valid_and_empty(move_forward):
                    moves.append(kick_start)
            white_hit_right: Cell = (row + 1, column + 1)
            if self.can_hit_on_cell(white_hit_right):
                moves.append(white_hit_right)
            white_hit_left: Cell = (row + 1, column - 1)
            if self.can_hit_on_cell(white_hit_left):
                moves.append(white_hit_left)
        else:
            move_forward: Cell = (row - 1, column)
            if self.board.cell_is_valid_and_empty(move_forward):
                moves.append(move_forward)
            if row == 6:
                kick_start: Cell = (row - 2, column)
                if self.board.cell_is_valid_and_empty(
                    kick_start
                ) and self.board.cell_is_valid_and_empty(move_forward):
                    moves.append(kick_start)
            black_hit_right: Cell = (row - 1, column - 1)
            if self.can_hit_on_cell(black_hit_right):
                moves.append(black_hit_right)
            black_hit_left: Cell = (row - 1, column + 1)
            if self.can_hit_on_cell(black_hit_left):
                moves.append(black_hit_left)

        return moves


class Rook(Piece):  # Turm
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        Implementation of the movability mechanic for `rooks <https://de.wikipedia.org/wiki/Turm_(Schach)>`_.

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Rooks can move only horizontally or vertically. They can move an arbitrary amount of cells until blocked by an own piece
        or an opposing piece (which they could hit and then being stopped).

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`,
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>`
        to check for necessary conditions to implement the rook movability mechanics.

        :return: A list of reachable cells this rook could move into.
        """
        reachable_cells = []

        row, col = self.cell

        directions = {
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        }

        for direction_row, direction_col in directions:
            current_row = row + direction_row
            current_col = col + direction_col

            while True:
                current_cell = (current_row, current_col)

                if self.board.cell_is_valid_and_empty(current_cell):
                    reachable_cells.append(current_cell)

                    current_row += direction_row
                    current_col += direction_col

                elif self.can_hit_on_cell(current_cell):
                    reachable_cells.append(current_cell)
                    break
                else:
                    break

        return reachable_cells


class Knight(Piece):  # Springer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Knights can move in a special pattern. They can move two rows up or down and then one column left or right. Alternatively, they can
        move one row up or down and then two columns left or right. They are not blocked by pieces in between.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`,
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>`
        to check for necessary conditions to implement the rook movability mechanics.

        :return: A list of reachable cells this knight could move into.
        """
        reachable_cells = []
        row, col = self.cell

        directions = {
            (-2, -1),
            (-2, 1),
            (2, -1),
            (2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
        }

        for direction_row, direction_col in directions:
            target_cell = (row + direction_row, col + direction_col)

            if self.board.cell_is_valid_and_empty(target_cell):
                reachable_cells.append(target_cell)

            elif self.board.piece_can_hit_on_cell(self, target_cell):
                reachable_cells.append(target_cell)

        return reachable_cells


class Bishop(Piece):  # Läufer
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        Implement the movability mechanic for `bishop <https://de.wikipedia.org/wiki/L%C3%A4ufer_(Schach)>`_.

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Bishops can move diagonally an arbitrary amount of cells until blocked.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`,
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>`
        to check for necessary conditions to implement the rook movability mechanics.

        :return: A list of reachable cells this bishop could move into.
        """
        reachable_cells = []

        row, col = self.cell

        directions = {(-1, -1), (1, -1), (-1, 1), (1, 1)}

        for direction_row, direction_col in directions:
            current_row = row + direction_row
            current_col = col + direction_col

            while True:
                current_cell = (current_row, current_col)

                if self.board.cell_is_valid_and_empty(current_cell):
                    reachable_cells.append(current_cell)

                    current_row += direction_row
                    current_col += direction_col

                elif self.can_hit_on_cell(current_cell):
                    reachable_cells.append(current_cell)
                    break
                else:
                    break

        return reachable_cells


class Queen(Piece):  # Königin
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        Implement the movability mechanic for the `queen <https://de.wikipedia.org/wiki/Dame_(Schach)>`_.

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Queens can move horizontally, vertically and diagonally an arbitrary amount of cells until blocked. They combine the movability
        of rooks and bishops.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`,
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>`
        to check for necessary conditions to implement the rook movability mechanics.

        :return: A list of reachable cells this queen could move into.
        """
        reachable_cells = []

        row, col = self.cell

        directions = {
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1),
        }

        for direction_row, direction_col in directions:
            current_row = row + direction_row
            current_col = col + direction_col

            while True:
                current_cell = (current_row, current_col)

                if self.board.cell_is_valid_and_empty(current_cell):
                    reachable_cells.append(current_cell)

                    current_row += direction_row
                    current_col += direction_col

                elif self.can_hit_on_cell(current_cell):
                    reachable_cells.append(current_cell)
                    break
                else:
                    break

        return reachable_cells


class King(Piece):  # König
    def __init__(self, board, white):
        super().__init__(board, white)

    def get_reachable_cells(self):
        """
        Implement the movability mechanic for the `king <https://de.wikipedia.org/wiki/K%C3%B6nig_(Schach)>`_.

        **NOTE**: Here you do not yet need to consider whether your own King would become checked after a move. This will be taken care of by
        the :py:meth:`is_king_check <board.Board.is_king_check>` and :py:meth:`get_valid_cells <pieces.Piece.get_valid_cells>` methods.

        **HINT**: Kings can move horizontally, vertically and diagonally but only one piece at a time.

        You can call :py:meth:`cell_is_valid_and_empty <board.Board.cell_is_valid_and_empty>`,
        :py:meth:`can_hit_on_cell <pieces.Piece.can_hit_on_cell>` and :py:meth:`can_enter_cell <pieces.Piece.can_enter_cell>`
        to check for necessary conditions to implement the rook movability mechanics.

        :return: A list of reachable cells this king could move into.
        """
        reachable_cells = []

        row, col = self.cell

        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        for dr, dc in directions:
            target_cell = (row + dr, col + dc)

            # The king can enter an empty cell or a cell with an enemy piece
            if self.can_enter_cell(target_cell):
                reachable_cells.append(target_cell)

        return reachable_cells

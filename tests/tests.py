import json
import unittest

from unittest_prettify.colorize import (
    RED,
    colorize,
)

from chess_ai.domain.board import Board, InvalidColumnException, InvalidRowException
from chess_ai.domain.pieces import Bishop, King, Knight, Pawn, Queen, Rook
from chess_ai.engine import MinMaxArg, evaluate_all_possible_moves
from chess_ai.util.helpers import (
    cell_to_string,
    map_piece_to_character,
    map_piece_to_fullname,
)


def iterate_pieces(board):
    for row in board.cells:
        for piece in row:
            if piece is None:
                continue

            yield piece


def print_movability_error(board, piece, cell, positiveMovement):
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    RESET = "\x1b[37m"
    text = RED + "Movability wrongly implemented. In this configuration\n\n"
    for row in range(7, -1, -1):
        text += "        " + RESET + f"{row+1} "
        for col in range(8):
            color = RESET
            if piece.cell[0] == row and piece.cell[1] == col:
                color = RED
            if cell[0] == row and cell[1] == col:
                color = GREEN

            text += color + map_piece_to_character(board.get_cell((row, col))) + " "
        text += "\n"

    files = ["a", "b", "c", "d", "e", "f", "g", "h"]
    text += "          "
    for col in range(8):
        text += f"{files[col]} "

    text += "\n\n"
    center = (
        " should be able to move to "
        if positiveMovement
        else " should not be able to move to "
    )
    text += (
        RED
        + map_piece_to_fullname(piece)
        + " on "
        + cell_to_string(piece.cell)
        + " (red)"
        + center
        + cell_to_string(cell)
        + " (green)."
    )
    text += "\n" + RESET

    print(text)


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board.reset()

    # ---------------------------------------------------------------------------
    # Phase A – Board-Basics
    # ---------------------------------------------------------------------------

    @colorize(color=RED)
    def test_A01_set_cell_exceptions(self):
        with self.assertRaises(InvalidRowException) as context:
            self.board.set_cell((-1, 0), None)

        with self.assertRaises(InvalidColumnException) as context:
            self.board.set_cell((0, -1), None)

        self.board.reset()

        piece = self.board.get_cell((0, 0))
        self.board.set_cell((3, 4), piece)

        self.assertIsNone(
            self.board.get_cell((0, 0)),
            "set_cell should set origin cell of piece to None",
        )
        self.assertEqual(piece.cell[0], 3, "set_cell should set piece cell correctly")
        self.assertEqual(piece.cell[1], 4, "set_cell should set piece cell correctly")
        newPiece = self.board.get_cell((3, 4))
        self.assertEqual(piece, newPiece, "set_cell should set piece cell correctly")
        self.assertIsNone(
            self.board.get_cell((0, 0)),
            "set_cell should set origin cell of piece to None",
        )

        self.board.set_cell((0, 7), None)
        newPiece = self.board.get_cell((0, 7))
        self.assertIsNone(newPiece, "set_cell should set piece cell correctly")

    @colorize(color=RED)
    def test_A02_get_cell(self):
        self.assertIsNone(
            self.board.get_cell((-1, -1)),
            "get_cell should return None for invalid cells",
        )
        self.assertIsNone(
            self.board.get_cell((3, 3)), "get_cell should return None for empty cells"
        )

        piece = self.board.get_cell((0, 0))
        self.assertIsNotNone(piece, "get_cell should return proper piece")
        self.assertTrue(isinstance(piece, Rook), "get_cell should return proper piece")
        self.assertTrue(piece.white, "get_cell should return proper piece")
        row, col = piece.cell
        self.assertEqual(row, 0, "get_cell should return proper piece")
        self.assertEqual(col, 0, "get_cell should return proper piece")

    @colorize(color=RED)
    def test_A03_none_is_not_valid_cell(self):
        """board.is_valid_cell() should return False is called with cell==None"""
        self.assertFalse(
            self.board.is_valid_cell(None), "None should not be a valid cell!"
        )

    @colorize(color=RED)
    def test_A04_valid_cells_inside(self):
        """board.is_valid_cell() should return True for all cells in range (0..7, 0..7) (64 cells in total)"""
        for row in range(8):
            for col in range(8):
                self.assertTrue(
                    self.board.is_valid_cell((row, col)),
                    f"({row}, {col}) should be a valid cell!",
                )

    @colorize(color=RED)
    def test_A05_valid_cells_outside(self):
        """board.is_valid_cell() should return False for all cells in range not in (0..7, 0..7)"""
        for row in range(-4, 12):
            for col in range(-4, 12):
                if row >= 0 and row < 8 and col >= 0 and col < 8:
                    continue

                self.assertFalse(
                    self.board.is_valid_cell((row, col)),
                    f"({row}, {col}) should not be a valid cell!",
                )

    @colorize(color=RED)
    def test_A06_cell_is_valid_and_empty(self):
        """board.cell_is_valid_and_empty() should return True for empty cells and False for used cells or invalid cells"""
        for row in range(8):
            for col in range(8):  # Go over all 8 columns
                if (
                    row <= 1 or row >= 6
                ):  # First two rows and last two rows are not empty
                    self.assertFalse(
                        self.board.cell_is_valid_and_empty((row, col)),
                        f"({row}, {col}) should not be empty!",
                    )
                else:  # Center six rows are empty
                    self.assertTrue(
                        self.board.cell_is_valid_and_empty((row, col)),
                        f"({row}, {col}) should be valid and empty!",
                    )

        # Test invalid cells as well
        for row in range(-4, 12):
            for col in range(-4, 12):
                if row >= 0 and row < 8 and col >= 0 and col < 8:
                    continue

                self.assertFalse(
                    self.board.is_valid_cell((row, col)),
                    f"({row}, {col}) should not be a valid cell!",
                )

    @colorize(color=RED)
    def test_A07_piece_can_enter(self):
        """board.piece_can_enter_cell() should behave correctly for white and black pieces"""
        # Start with a white pawn, he can enter all of the 6 top rows but none of the bottom two rows
        piece = Pawn(self.board, True)

        for row in range(8):
            for col in range(8):  # Go over all 8 columns
                if row <= 1:  # First two rows are white pieces, pawn cannot enter
                    self.assertFalse(
                        self.board.piece_can_enter_cell(piece, (row, col)),
                        f"White pieces should not be able to enter ({row}, {col}) as there is another white piece!",
                    )
                else:  # Center six rows are empty
                    self.assertTrue(
                        self.board.piece_can_enter_cell(piece, (row, col)),
                        f"White pieces should be able to enter ({row}, {col}) as there is no white piece yet!",
                    )

        # Now do the same for a black pawn
        piece = Pawn(self.board, False)

        for row in range(8):
            for col in range(8):  # Go over all 8 columns
                if row >= 6:  # Top two rows are black pieces, pawn cannot enter
                    self.assertFalse(
                        self.board.piece_can_enter_cell(piece, (row, col)),
                        f"Black pieces should not be able to enter ({row}, {col}) as there is another black piece!",
                    )
                else:  # Center six rows are empty
                    self.assertTrue(
                        self.board.piece_can_enter_cell(piece, (row, col)),
                        f"Black pieces should be able to enter ({row}, {col}) as there is no black piece yet!",
                    )

        # Test invalid cells as well
        for row in range(-4, 12):
            for col in range(-4, 12):
                if row >= 0 and row < 8 and col >= 0 and col < 8:
                    continue

                self.assertFalse(
                    self.board.is_valid_cell((row, col)),
                    f"({row}, {col}) should not be enterable as it is not a valid cell!",
                )

    @colorize(color=RED)
    def test_A08_piece_can_hit_on_cell(self):
        """board.piece_can_hit_on_cell() should behave correctly for white and black pieces"""
        # Start with a white pawn, he can hit all of the 2 top rows but none of the rows below
        piece = Pawn(self.board, True)

        for row in range(8):
            for col in range(8):  # Go over all 8 columns
                if (
                    row <= 5
                ):  # Everything except top two rows do not contain black pieces
                    self.assertFalse(
                        self.board.piece_can_hit_on_cell(piece, (row, col)),
                        f"White pieces should not be able to hit on ({row}, {col}) as there is no black piece!",
                    )
                else:
                    self.assertTrue(
                        self.board.piece_can_hit_on_cell(piece, (row, col)),
                        f"White pieces should be able to hit ({row}, {col}) as there is a black piece!",
                    )

        # Now do the same for a black pawn
        piece = Pawn(self.board, False)

        for row in range(8):
            for col in range(8):  # Go over all 8 columns
                if (
                    row >= 2
                ):  # Everything but bottom two rows do not contain white pieces
                    self.assertFalse(
                        self.board.piece_can_hit_on_cell(piece, (row, col)),
                        f"Black pieces should not be able to hit on ({row}, {col}) as there is no white piece!",
                    )
                else:  # Center six rows are empty
                    self.assertTrue(
                        self.board.piece_can_hit_on_cell(piece, (row, col)),
                        f"Black pieces should be able to hit on ({row}, {col}) as there is a white piece!",
                    )

        # Test invalid cells as well
        for row in range(-4, 12):
            for col in range(-4, 12):
                if row >= 0 and row < 8 and col >= 0 and col < 8:
                    continue

                self.assertFalse(
                    self.board.is_valid_cell((row, col)),
                    f"Should not be able to hit on ({row}, {col}) as it is not a valid cell!",
                )

    # ---------------------------------------------------------------------------
    # Phase B – Figurenlogik, König & Evaluation
    # ---------------------------------------------------------------------------

    @colorize(color=RED)
    def test_B01_movability(self):
        # Load JSON Test Suite
        with open("tests/fixtures/movement_test.json", "rt") as f:
            suite = json.load(f)

        # Iterate all test cases
        for testcase in suite["testcases"]:
            # Load the configuration from disk
            self.board.load_from_disk("tests/fixtures/" + testcase["configuration"])

            movability = testcase["movability"]

            # Now iterate all pieces and check if their actual movability matches the ground truth
            for piece in iterate_pieces(self.board):
                # Write cell in clear text
                key = cell_to_string(piece.cell)

                # Only the test movability we are supposed to test in the test case
                if key not in movability:
                    continue

                # Get ground truth from file, turn into a set
                groundTruth = {(row, col) for row, col in movability[key]}

                # Get actually reachable cells, turn into a set
                actual = {
                    (int(row), int(col)) for row, col in piece.get_reachable_cells()
                }

                # If they match, all is fine
                for cell in groundTruth:
                    if cell in actual:
                        continue

                    # If not, output a meaningful message
                    print("\nTestcase name: ", testcase["name"])
                    print_movability_error(self.board, piece, cell, True)
                    self.fail(
                        f"Movement of the {map_piece_to_fullname(piece)} wrongly implemented!"
                    )

                # If they match, all is fine
                for cell in actual:
                    if cell in groundTruth:
                        continue

                    # If not, output a meaningful message
                    print("\nTestcase name: ", testcase["name"])
                    print_movability_error(self.board, piece, cell, False)

                    self.fail(
                        f"Movement of the {map_piece_to_fullname(piece)} wrongly implemented!"
                    )

    @colorize(color=RED)
    def test_B02_iterate_pieces_empty_board(self):
        self.board.clear_board()

        for color in [True, False]:
            for _ in self.board.iterate_cells_with_pieces(color):
                self.fail(
                    "board.iterate_cells_with_pieces should not yield anything on an empty board!"
                )

    @colorize(color=RED)
    def test_B03_iterate_pieces(self):
        for color in [True, False]:
            # Count total pieces
            total = 0

            # Iterate white pieces
            for piece in self.board.iterate_cells_with_pieces(color):
                # Unpack cell tuple
                row, col = piece.cell

                if color is True:  # White pieces need to be on row 0 or 1
                    self.assertLessEqual(
                        piece.cell[0],
                        1,
                        "board.iterate_cells_with_pieces yields wrongly places pieces",
                    )
                else:  # Black pieces need to be on row 6 or 7
                    self.assertGreaterEqual(
                        piece.cell[0],
                        6,
                        "board.iterate_cells_with_pieces yields wrongly places pieces",
                    )

                self.assertEqual(
                    piece.white,
                    color,
                    "board.iterate_cells_with_pieces yields pieces of wrong color",
                )
                total += 1

            # Make sure we got iterated exactly 16 pieces
            if total < 16:
                self.fail("board.iterate_cells_with_pieces does not yield all pieces")
            elif total > 16:
                self.fail("board.iterate_cells_with_pieces does too many pieces")

    @colorize(color=RED)
    def test_B04_find_king(self):
        for color in [True, False]:
            piece = self.board.find_king(color)
            self.assertIsNotNone(piece, "board.find_king does not yield the King piece")
            self.assertTrue(
                isinstance(piece, King),
                "board.find_king must only yield the King piece",
            )
            self.assertEqual(
                piece.white,
                color,
                "board.find_king must not yield wrongly colored king piece",
            )

        self.board.clear_board()
        self.assertIsNone(
            self.board.find_king(True),
            "board.find_king must not yield a piece on an empty board",
        )
        self.assertIsNone(
            self.board.find_king(False),
            "board.find_king must not yield a piece on an empty board",
        )

    @colorize(color=RED)
    def test_B05_king_in_check(self):
        self.board.load_from_memory(
            """. . . . . . . .
         . . . . . K . .
         . . . . . . . .
         . . . . n . . .
         . . . . . . . .
         . . . . . k . .
         . . . . . . . .
         . . . . . . . ."""
        )

        self.assertTrue(
            self.board.is_king_check(True),
            "is_king_check does not properly identify king being in check!",
        )
        self.assertFalse(
            self.board.is_king_check(False),
            "is_king_check should not report unchecked king as being checked!",
        )

        self.board.load_from_memory(
            """. . . . . . . .
         . . . . . Q . .
         . . . . . . . .
         . . . . . . . .
         . . k . . K . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . ."""
        )

        self.assertFalse(
            self.board.is_king_check(True),
            "is_king_check should not report unchecked king as being checked!",
        )
        self.assertTrue(
            self.board.is_king_check(False),
            "is_king_check does not properly identify king being in check!",
        )

        self.board.load_from_memory(
            """. . . . . . . .
         . . . . . . . .
         . . k . . . . .
         . P . . . . p .
         . . . . . K . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . ."""
        )

        self.assertTrue(
            self.board.is_king_check(True),
            "is_king_check does not properly identify king being in check!",
        )
        self.assertTrue(
            self.board.is_king_check(False),
            "is_king_check does not properly identify king being in check!",
        )

    @colorize(color=RED)
    def test_B06_evaluate(self):
        self.board.reset()
        self.assertAlmostEqual(
            self.board.evaluate(),
            0,
            msg="Evaluate should return 0 on the default board configuration.",
        )

        self.board.clear_board()
        self.assertAlmostEqual(
            self.board.evaluate(), 0, msg="Evaluate should return 0 on an empty board."
        )

        self.board.load_from_memory(
            """. . . . k . . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . .
         P P P P P P P P
         R N B Q K B N R"""
        )

        self.assertGreater(
            self.board.evaluate(),
            0,
            msg="Evaluate should return a positive value if white is dominanting.",
        )

        self.board.load_from_memory(
            """r n b q k b n r
         p p p p p p p p
         . . . . . . . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . .
         . . . . . . . .
         . . . . K . . ."""
        )

        self.assertLess(
            self.board.evaluate(),
            0,
            msg="Evaluate should return a negative value if black is dominanting.",
        )

    @colorize(color=RED)
    def test_B07_get_valid_moves_leaves_board_intact(self):
        # Load a configuration from disk
        self.board.load_from_disk("tests/fixtures/random1.board")

        # Hash it for later reference
        beforeHash = self.board.hash()

        # Iterate over all pieces
        for piece in iterate_pieces(self.board):
            # Get all valid moves for this piece
            valid_moves = piece.get_valid_cells()

            # Now make sure the board configuration did not change
            self.assertEqual(
                beforeHash,
                self.board.hash(),
                "piece.get_valid_cells must not alter board configuration after its return",
            )

    # ---------------------------------------------------------------------------
    # Phase C – Engine / MinMax-Einbindung
    # ---------------------------------------------------------------------------

    @colorize(color=RED)
    def test_C01_evaluate_all_possible_moves_empty_list_on_empty_board(self):
        self.board.clear_board()

        moves = evaluate_all_possible_moves(self.board, minMaxArg=MinMaxArg())
        self.assertTrue(
            not moves,
            "evaluate_all_possible_moves should return an empty list for an empty board",
        )

    @colorize(color=RED)
    def test_C02_evaluate_all_possible_moves_ten_moves(self):
        self.board.load_from_memory(
            """. . . . . . . K
         . . . . . . . .
         . . . p . . . .
         . . . . . . . .
         . b . R . q . .
         . . . . . . . .
         . . . k . . . .
         . . . . . . . ."""
        )

        moves = evaluate_all_possible_moves(self.board, minMaxArg=MinMaxArg())
        self.assertEqual(
            len(moves),
            10,
            "evaluate_all_possible_moves should return exactly 10 moves in this configuration for White.\n\n"
            + str(self.board),
        )

        self.assertTrue(
            isinstance(moves[0].piece, Rook),
            "Top move for white should be hitting with the rook in this case!\n\n"
            + str(self.board),
        )
        self.assertTrue(
            isinstance(self.board.get_cell(moves[0].cell), King),
            "Top move for white should be hitting the black king in this case!\n\n"
            + str(self.board),
        )

        self.assertTrue(
            isinstance(moves[1].piece, Rook),
            "2nd top move for white should be hitting with the rook in this case!\n\n"
            + str(self.board),
        )
        self.assertTrue(
            isinstance(self.board.get_cell(moves[1].cell), Queen),
            "2nd top move for white should be hitting the black queen in this case!\n\n"
            + str(self.board),
        )

        self.assertTrue(
            isinstance(moves[2].piece, Rook),
            "3rd top move for white should be hitting with the rook in this case!\n\n"
            + str(self.board),
        )
        self.assertTrue(
            isinstance(self.board.get_cell(moves[2].cell), Bishop),
            "3rd top move for white should be hitting the black bishop in this case!\n\n"
            + str(self.board),
        )

        self.assertTrue(
            isinstance(moves[3].piece, Rook),
            "4th top move for white should be hitting with the rook in this case!\n\n"
            + str(self.board),
        )
        self.assertTrue(
            isinstance(self.board.get_cell(moves[3].cell), Pawn),
            "4th top move for white should be hitting the black pawn in this case!\n\n"
            + str(self.board),
        )

    @colorize(color=RED)
    def test_C03_evaluate_all_possible_moves_random_config_order(self):
        self.board.load_from_disk("tests/fixtures/random1.board")

        moves = evaluate_all_possible_moves(
            self.board, minMaxArg=MinMaxArg(playAsWhite=True), maximumNumberOfMoves=500
        )
        for index in range(len(moves) - 1):
            self.assertGreaterEqual(
                moves[index].score,
                moves[index + 1].score,
                "evaluate_all_possible_moves should return sorted list in descending order when playing as White",
            )

        moves = evaluate_all_possible_moves(
            self.board, minMaxArg=MinMaxArg(playAsWhite=False), maximumNumberOfMoves=500
        )
        for index in range(len(moves) - 1):
            self.assertLessEqual(
                moves[index].score,
                moves[index + 1].score,
                "evaluate_all_possible_moves should return sorted list in ascending order when playing as Black",
            )

    @colorize(color=RED)
    def test_C04_evaluate_all_possible_moves_random_config_truncated(self):
        self.board.load_from_disk("tests/fixtures/random1.board")

        moves = evaluate_all_possible_moves(
            self.board, minMaxArg=MinMaxArg(playAsWhite=True), maximumNumberOfMoves=6
        )
        self.assertEqual(
            len(moves),
            6,
            "evaluate_all_possible_moves should respect requested amount of moves",
        )


if __name__ == "__main__":
    unittest.main()

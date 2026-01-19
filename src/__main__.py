import argparse
import sys
import unittest

import test_runner
from board import Board
from ui import run_game


def run_tests():
    print("🧪 Starte Unittests...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_runner)
    runner = unittest.TextTestRunner(verbosity=3)
    runner.failfast = False
    result = runner.run(suite)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Starte das Schachspiel mit verschiedenen Modi"
    )
    parser.add_argument(
        "--mode",
        choices=["manual", "ai", "test"],
        required=True,
        help="Modus auswählen: 'manual' (Mensch gegen Mensch), 'ai' (gegen KI spielen), 'test' (Unit-Tests ausführen)",
    )

    args = parser.parse_args()

    if args.mode == "manual":
        board = Board()
        board.reset()
        run_game(board, True)
    elif args.mode == "ai":
        board = Board()
        board.reset()
        run_game(board, False)
    elif args.mode == "test":
        run_tests()


if __name__ == "__main__":
    main()

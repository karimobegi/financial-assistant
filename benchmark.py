from statistics import median, mean

from adversary import RandomAdversary
from board import Board
from player import SelectedPlayer
from constants import BOARD_WIDTH, BOARD_HEIGHT, BLOCK_LIMIT
from exceptions import BlockLimitException


def run_one_game(seed: int) -> int:
    """Run one full game with a given seed, return the final score."""
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(seed, BLOCK_LIMIT)
    player = SelectedPlayer()   # this is your myTetrisAI

    try:
        # just run until game over or block limit, ignore the moves
        for _ in board.run(player, adversary):
            pass
    except BlockLimitException:
        # this just means we used all blocks; board.score is still valid
        pass

    return board.score


def main():
    # choose whatever range of seeds you like
    seeds = list(range(100, 120))   # 20 runs: 100, 101, ..., 119

    scores = []
    for s in seeds:
        score = run_one_game(s)
        scores.append(score)
        print(f"Seed {s}: score = {score}")

    print("\n--- Summary ---")
    print(f"Seeds tested: {len(seeds)}")
    print(f"Scores: {scores}")
    print(f"Mean score  : {mean(scores):.1f}")
    print(f"Median score: {median(scores):.1f}")


if __name__ == "__main__":
    main()
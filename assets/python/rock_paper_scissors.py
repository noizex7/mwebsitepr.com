"""Challenge the computer to Rock, Paper, Scissors."""
import random

MOVES = ["rock", "paper", "scissors"]
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}


def ask_player():
    choice = input("Choose rock, paper, or scissors: ").strip().lower()
    if choice not in MOVES:
        raise ValueError("Please choose rock, paper, or scissors.")
    return choice


def main():
    print("Rock, Paper, Scissors")
    rounds = int(input("How many rounds? (default 3) ") or "3")
    player_score = 0
    computer_score = 0

    for number in range(1, rounds + 1):
        print(f"\nRound {number}")
        try:
            player_move = ask_player()
        except ValueError as exc:
            print(exc)
            continue
        computer_move = random.choice(MOVES)
        print("Computer picked:", computer_move)
        if player_move == computer_move:
            print("Tie round.")
        elif BEATS[player_move] == computer_move:
            print("You win the round!")
            player_score += 1
        else:
            print("Computer wins the round.")
            computer_score += 1

    print("\nFinal score - You:", player_score, "Computer:", computer_score)
    if player_score > computer_score:
        print("Congratulations, you win!")
    elif player_score < computer_score:
        print("Computer takes the match. Try again!")
    else:
        print("It's a tie overall.")


if __name__ == "__main__":
    main()

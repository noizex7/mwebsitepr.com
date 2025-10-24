"""Play a quick round of hangman."""
import random

WORDS = [
    "python",
    "portfolio",
    "automation",
    "developer",
    "cloud",
    "docker",
]


def reveal_word(secret, guesses):
    return " ".join(letter if letter in guesses else "_" for letter in secret)


def main():
    secret = random.choice(WORDS)
    guesses = set()
    attempts = 6

    print("Hangman Game")
    print("I picked a word with", len(secret), "letters.")

    while attempts > 0:
        print("\nWord:", reveal_word(secret, guesses))
        print("Attempts left:", attempts)
        guess = input("Pick a letter: ").strip().lower()
        if not guess:
            print("Please type a letter.")
            continue
        if len(guess) != 1 or not guess.isalpha():
            print("Only single letters are allowed.")
            continue
        if guess in guesses:
            print("You already tried that one.")
            continue

        guesses.add(guess)
        if guess in secret:
            print("Great guess!")
            if all(letter in guesses for letter in secret):
                print("\nYou solved it! The word was:", secret)
                break
        else:
            attempts -= 1
            print("Nope, that letter is not there.")
    else:
        print("\nOut of attempts. The word was:", secret)


if __name__ == "__main__":
    main()

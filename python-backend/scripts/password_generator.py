"""Create high-entropy passwords with optional symbols."""
import secrets
import string

ALPHABET = string.ascii_letters + string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{}"


def build_password(length=16, include_symbols=True):
    pool = ALPHABET + (SYMBOLS if include_symbols else "")
    if length < 4:
        raise ValueError("Pick a length of at least 4 characters")
    return "".join(secrets.choice(pool) for _ in range(length))


def ask_bool(prompt, default=False):
    answer = input(prompt).strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes", "true", "1"}


def main():
    print("Secure Password Generator")
    print("-" * 32)
    try:
        raw_length = input("How many characters? (default 16) ")
        length = int(raw_length or "16")
    except ValueError:
        print("That was not a number, using 16.")
        length = 16
    include_symbols = ask_bool("Include symbols? [y/N] ")
    try:
        password = build_password(length, include_symbols)
    except ValueError as exc:
        print(f"Could not build password: {exc}")
    else:
        print(f"Your password: {password}")


if __name__ == "__main__":
    main()

from string import ascii_letters
import random
name_length = 5
# There are 380,000,000+ possible names!


def main():
    f = open("RandomlyGeneratedCommitName.txt", "w+")

    name = ""
    char_amount = 0
    while char_amount < name_length:
        letter = andom.choice(ascii_letters)
        name += letter
        char_amount += 1

    f.write(name)


if __name__ == "__main__":
    main()

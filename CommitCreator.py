import subprocess
from string import ascii_letters
from random import choice
name_length = 5
# There are 380,000,000+ possible names!


def main():
    f = open("RandomlyGeneratedCommitName.txt", "w+")

    name = ""
    char_amount = 0
    while char_amount < name_length:
        letter = choice(ascii_letters)
        name += letter
        char_amount += 1

    f.write(name)
    subprocess.call('git add .'.split())
    subprocess.call(['git', 'commit', '-m', 'New commit for testing: ' + name])


if __name__ == "__main__":
    main()

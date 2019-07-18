import subprocess
from string import ascii_letters
from random import choice
from time import sleep
commits = 4
name_length = 5
# There are 380,000,000+ possible names!


def main():
    # f = open("RandomlyGeneratedCommitName.txt", "w+")

    name = ""
    char_amount = 0
    while char_amount < name_length:
        letter = choice(ascii_letters)
        name += letter
        char_amount += 1

    # f.write(name)
    subprocess.call('git add .'.split())
    subprocess.call(['git', 'commit', '--allow-empty', '-m', 'New commit for testing: ' + name])


if __name__ == "__main__":
    i = 0
    while i < commits:
        main()
        sleep(3)
        i += 1

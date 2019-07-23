import subprocess
from string import ascii_letters
from random import choice
from time import sleep
commits = 10
name_length = 5
# There are 380,000,000+ possible names!


def main():
    name = ""
    char_amount = 0
    while char_amount < name_length:
        letter = choice(ascii_letters)
        name += letter
        char_amount += 1

    subprocess.call('git add .'.split())
    subprocess.call(['git', 'commit', '--allow-empty', '-m', 'Dummy commit: ' + name])


if __name__ == "__main__":
    i = 0
    while i < commits:
        main()
        sleep(1)
        i += 1

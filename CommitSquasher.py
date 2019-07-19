import sys
import argparse
from subprocess import Popen, STDOUT, PIPE
from time import sleep

seperator = "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #"
main_branch = "yeetus"
commit_branch = main_branch + "_CommitSquasher"

parser = argparse.ArgumentParser(description="Squash a specified amount of commits on this branch. The commits "
                                             "considered start at HEAD and get older.")
parser.add_argument('message', metavar='M', type=str, nargs='?',
                    help='The message to give the commit made of squashed commits. Must be in quotes when calling this '
                         'script.')
parser.add_argument('squash_num', metavar='N', type=int, nargs='?',
                    help='The number of commits (including the HEAD commit) to squash.')


def git(*arguments):
    print(arguments)
    cmdline = ['git']
    cmdline.extend(arguments)

    print(' '.join(arg for arg in cmdline))

    proc = Popen(cmdline, stdout=PIPE, stderr=STDOUT)
    print('')
    output = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break

        line = line.rstrip().decode('utf-8')
        print('git> {0}'.format(line))
        output.append(line)

    print()
    return_code = proc.wait()
    if return_code != 0:
        print()
        print('Git command terminated with exit code {0}.'.format(return_code))
        sys.exit(1)

    return output


def main(args):
    print('Prepare to "squash" some commits.')

    if args.message:
        print(args.message)

    # Get the amount of commits (including current) to squash
    squash_amount = 0
    # Use clargs
    if args.squash_num and args.squash_num > 1:
        squash_amount = args.squash_num
    # Use user using user input
    while squash_amount <= 1:
        print("How many commits (including the current one) on this branch will you squash?")
        try:
            squash_amount = int(input("Two minimum "))
        except ValueError:
            print("Invalid input")
            print(seperator)
            squash_amount = 0

    git('fetch', 'origin')

    # Get the hashes of the commits requested for squashing (7 character versions)
    # If squash_amount is higher than the amount of what's available, it'll automatically get everything
    hashes = git('log', '--pretty=format:%h')[:squash_amount]

    # Make a list of their messages
    messages = []
    for h in hashes:
        message = git('show', '--no-patch', '--format=%B', h)[0]
        messages.append(message)

    # TODO possibly: With the two most recent git commands, the user will see a list of all the hashes and messages of
    #  the requested commits. Use this command to print more detail:
    # git('log', '--graph', '--decorate', '--oneline')

    # Print the messages
    print(seperator)
    print("Messages of commits to be squashed (new to old):")
    print(seperator)
    for message in messages:
        print(message)

    # Get a new message for the new commit
    print("\n" + seperator)
    new_mes = get_new_message(messages, args.message)
    confirm_squash(new_mes)

    # Squash the squash
    squash(hashes[len(hashes) - 1], new_mes)
    print(seperator)
    input("Squashing complete. Enter to quit.")


# Returns a new message for a commit determined by user input
# The user can write a new message, combine 'olds', or use the latest message in 'olds'
# 'olds' should be the current list of commits to be squashed
def get_new_message(olds, arg_message):
    new = ""
    # Set the message to one given in the command line, if possible
    if arg_message:
        new = arg_message
        return new
    # Otherwise, get one from the user
    write_new = input("Write a completely new message for the squashed commit? (y/n) ").lower()
    if 'y' == write_new:
        # TODO: Figure out a way of accepting multi-line input (maybe that one with Ctrl+D?)
        new = input("Write new message below, enter to submit.\n")
        print("Message received.")

    elif 'n' == write_new:
        use_latest = input("Use latest message? (y) Or combine all messages? (any other input) ").lower()
        # Combine messages
        if 'y' == use_latest:
            print("Using latest message.")
            new = olds[0]

        # Use the latest message
        else:
            print("Combining messages...")
            for m in olds:
                new += m + "\n---\n"
            new = new[:-5]

    else:
        print("Input not accepted, cancelling squash.")
        quit()

    # Make sure the message isn't empty or blank by saying that there's no message, thus giving it a message
    # ...but there's still no message
    if "" == new.replace(' ', ''):
        new = "[No message]"
    return new


# Prints the message set for the new commit and waits for user input to continue
# 'message' is the new commit's set message
def confirm_squash(message):
    print("\n" + seperator)
    print("Squashed commit message:")
    print(seperator)
    print(message)
    print("\n" + seperator)
    input("Squashing will add and commit any unstaged changes.\n"
          "Enter to begin squash....")
    print(seperator)


# Create the squashed commit in a temporary branch, revert commits in the main one, then cherry-pick the squashed commit
# 'oldest_hash' is the SHA of the oldest commit to squash
# 'squash_mes' is the new commit's message
def squash(oldest_hash, squash_mes):
    # Save and commit the files to the current branch so a temporary one can be checked out
    # TODO: Give the user a choice between adding or dropping unstaged files
    git('checkout', main_branch)
    git('add', '.')
    git('commit', '--allow-empty', '-m', 'Saving changes for: ' + squash_mes)
    sleep(1)
    git('checkout', '-b', commit_branch)
    sleep(3)
    # Save changes in the actual squashed commit on this temp branch
    git('commit', '--allow-empty', '-m', squash_mes)
    sleep(1)
    # Hash of the squashed commit that was just made:
    new_hash = git('log', '--pretty=format:%h')[0]
    # Return to the main branch, reset over the the "squashing" commits, then bring the actual commit over
    git('checkout', main_branch)
    sleep(3)
    git('reset', oldest_hash + '^')
    git('cherry-pick', '--allow-empty', new_hash)
    sleep(1)
    # Delete the temporary branch
    git('branch', '-D', commit_branch)


if __name__ == "__main__":
    clargs = parser.parse_args()
    main(clargs)

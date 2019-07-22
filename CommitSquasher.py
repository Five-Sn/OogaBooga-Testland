import sys
import argparse
from subprocess import Popen, STDOUT, PIPE
import os

# Note: When manually squashing commits with an editor, you can still checkout the commits you squashed afterward. The
# same happens with this script, so if manual squashing saves space, then I feel like this must as well.

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


# Runs a git command, prints it and the result, and returns a list of lines in the result
# ex. git('pull', '--force')
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

    proc.kill()
    return output


def main(args):
    # Let the user change the repo if they want
    print("Currently in directory " + os.getcwd())
    new_dir = input("Enter new directory (empty for no change):\n").replace(' ', '')
    if new_dir != "":
        os.chdir(new_dir)

    # Change branch
    global main_branch
    global commit_branch
    print("Currently prepared to checkout " + main_branch)
    new_branch = input("Enter new branch (empty for no change):\n")
    if new_branch != "":
        main_branch = new_branch
        commit_branch = main_branch + "_CommitSquasher"

    git('checkout', main_branch)
    print(seperator)
    print('Prepare to "squash" some commits.')

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

    # With the two most recent git commands^, the user will see a list of all the hashes and messages of the requested
    # commits. Use this command to print more detail:
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
    add_or_drop(new_mes)
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
        # Get multiple lines of input, then add them together for the message
        print('Write a new message below, Ctrl+D to submit, write "done" on last line.')
        contents = []
        while True:
            # Ctrl + D interrupts input()
            msg_line = input()
            if msg_line == "done":
                break
            contents.append(msg_line)
        new = "\n".join(contents)

    elif 'n' == write_new:
        use_latest = input("Use latest message (y) or combine all messages? (any other input) ").lower()
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


# If there are unstaged changes, add or drop them (whichever the user says)
# TODO: I'm pretty sure this works, but more testing couldn't hurt
def add_or_drop(squash_mes):
    print("Cool")
    status = git('status')
    if check_lines(status, "Changes not staged for commit") is True:
        print("There are unstaged changes on this branch.")
        do_add = input("Stage and commit (y) or drop unstaged files? (any other input) ").lower()
        if 'y' == do_add:
            print("Adding changes...")
            git('add', '.')
        else:
            print("Dropping changes...")
            git('stash', 'save', '--keep-index', '--include-untracked')
            git('stash', 'drop')

    print("Committing if there are staged changes....")
    git('commit', '-m', 'Saving changes for: ' + squash_mes)


# Searched the list lst for an index that matches desired
def check_lines(lst, desired):
    for line in lst:
        if desired in line:
            return True
    return False


# Create the squashed commit in a temporary branch, revert commits in the main one, then cherry-pick the squashed commit
# 'oldest_hash' is the SHA of the oldest commit to squash
# 'squash_mes' is the new commit's message
def squash(oldest_hash, squash_mes):
    # Save and commit the files to the current branch so a temporary one can be checked out
    git('checkout', '-b', commit_branch)
    # Save changes in the actual squashed commit on this temp branch
    git('commit', '--allow-empty', '-m', squash_mes)
    # Hash of the squashed commit that was just made:
    new_hash = git('log', '--pretty=format:%h')[0]
    # Return to the main branch, reset over the the "squashing" commits, then bring the actual commit over
    git('checkout', main_branch)
    git('reset', oldest_hash + '^')
    git('cherry-pick', '--allow-empty', new_hash)
    # Delete the temporary branch
    git('branch', '-D', commit_branch)


if __name__ == "__main__":
    clargs = parser.parse_args()
    main(clargs)

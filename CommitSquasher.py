import sys
from subprocess import Popen, STDOUT, PIPE
from time import sleep

# TODO: add clargs and parseargs for the choices the user makes

seperator = "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #"
main_branch = "yeetus"
commit_branch = main_branch + "_CommitSquasher"


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


def main():
    print('Prepare to squash some commits.')

    # Get the amount of commits (including current) to squash
    squash_amount = 0
    while squash_amount <= 1:
        print("How many commits (including the current one) on this branch will you squash?")
        try:
            squash_amount = int(input("Two minimum "))
        except:
            print("Invalid input")
            squash_amount = 0

    git('fetch', 'origin')

    # TODO: With the next two git commands, the user will see a list of all the hashes and messeges of the requested
    #  commits. Use the commented-out command between them for more detail

    # Get the first 7 characters of the hashes of the requested commits
    # If squash_amount is higher than the amount of what's available, it'll just get everything
    hashes = git('log', '--pretty=format:%h')[:squash_amount]
    # git('log', '--graph', '--decorate', '--oneline')
    # Make a list of their messages
    messages = []
    for h in hashes:
        message = git('show', '--no-patch', '--format=%B', h)[0]
        messages.append(message)

    # Print the messages
    print(seperator)
    print("Messages of commits to be squashed (new to old):")
    print(seperator)
    for message in messages:
        print(message)

    # Get a new message for the new commit
    print("\n" + seperator)
    new_mes = get_new_message(messages)
    confirm_squash(new_mes)

    squash(hashes, new_mes)
    print(seperator)
    input("Squashing complete. Press enter to quit.")

    '''# Save and commit the files to the current branch so a temporary one can be checked out
    # TODO: Maybe don't add EVERYTHING. What to add instead? I dunno. Adding all used to be for making commits unique
    #  so they could actually be commited.
    git('checkout', main_branch)
    git('add', '.')
    git('commit', '--allow-empty', '-m', 'Saving changes for: ' + new_mes)
    sleep(1)
    git('checkout', '-b', commit_branch)
    sleep(3)
    # Save changes in the actual squashed commit on this temp branch
    git('commit', '--allow-empty', '-m', new_mes)
    sleep(1)
    # Hash of the squashed commit that was just made:
    new_hash = git('log', '--pretty=format:%h')[0]
    # Return to the main branch, reset over the the "squashing" commits, then bring the actual commit over
    git('checkout', main_branch)
    sleep(3)
    git('reset', hashes[len(hashes)-1] + '^')
    git('cherry-pick', '--allow-empty', new_hash)
    sleep(1)
    # Delete the temporary branch
    git('branch', '-D', commit_branch)'''


# Returns a new message for a commit determined by user input and/or
# 'olds' should be the current list of commits to be squashed
# The user can write a new message, combine 'olds', or use the latest message in 'olds'
def get_new_message(olds):
    new = ""
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
def confirm_squash(message):
    print("\n" + seperator)
    print("Squashed commit message:")
    print(seperator)
    print(message)
    print("\n" + seperator)
    input("Squashing will add and commit any unstaged changes.\n"
          "Enter to begin squash")
    print(seperator)


def squash(SHA_list, squash_mes):
    # Save and commit the files to the current branch so a temporary one can be checked out
    # TODO: Maybe don't add EVERYTHING. What to add instead? I dunno. Adding all used to be for making commits unique
    #  so they could actually be commited.
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
    git('reset', SHA_list[len(SHA_list) - 1] + '^')
    git('cherry-pick', '--allow-empty', new_hash)
    sleep(1)
    # Delete the temporary branch
    git('branch', '-D', commit_branch)


if __name__ == "__main__":
    main()

import sys
from subprocess import Popen, STDOUT, PIPE
from time import sleep

# TODO: add clargs and parseargs for the choices the user makes
# gnarly nasty

seperator = "# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #"


def git(*arguments):
    print(arguments)
    cmdline = ['git']
    cmdline.extend(arguments)

    # print('!GIT COMMAND!')
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

    # print('!GIT COMMAND!')
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

    # Commit the current files with the message chosen above
    # TODO: Don't add EVERYTHING. What to add instead? I dunno. Adding all used to be for making commits unique so they
    #  could actually be commited.
    git('add', '.')
    git('commit', '--allow-empty', '-m', new_mes)

    # Sleep for one second to give time for the commit to go through
    sleep(1)

    # The commits list doesn't include the newest commit- now it's purely commits to delete
    for h in hashes:
        print(h)
        git('rebase', '--rebase-merges', '--onto', h + '^', h)


# narrow it down to the ones at index 1 and 2
# thingymabob = thingymabob[1:3]

# git branch -f master HEAD~3
# sets the master branch to being at the commit at HEAD~3

# git log --graph --decorate --oneline
# gets a list of commits with their SHA hash IDs
# these commits are all those of the current branch and whatever it inherited from branching off

# git rebase -p --onto xsha^ xsha
# deletes the commit with the hash xsha

# rev-parse HEAD gets the most recent commit's hash or something
# change HEAD to something else to get that commit's has or whatever


# Returns a new message for a commit determined by user input and/or
# 'olds' should be the current list of commits to be squashed
# The user can write a new message, combine 'olds', or use the latest message in 'olds'
def get_new_message(olds):
    new = ""
    write_new = input("Write a completely new message for the squashed commit? (y/n) ").lower()
    if 'y' == write_new:
        # TODO: Figure out a way of accepting multi-line input (maybe that one with Ctrl+D?)
        new = input("Write new message below, enter to submit\n")
        print("Message taken.")

    elif 'n' == write_new:
        use_latest = input("Use latest message? (y) Will combine all messages otherwise ").lower()
        # Combine messages
        if 'y' == use_latest:
            print("Using latest message")
            new = olds[0]

        # Use the latest message
        else:
            print("Combining messages...")
            for m in olds:
                new += m + "\n---\n"
            new = new[:-5]

    else:
        print("Input not accepted, cancelling squash")
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


if __name__ == "__main__":
    main()

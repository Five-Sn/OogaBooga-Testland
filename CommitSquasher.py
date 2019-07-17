import sys
from subprocess import Popen, STDOUT, PIPE
from time import sleep

# TODO: add clargs and parseargs for the choices the user makes

# TODO: let the user set squash_amount
# The amount of commits to squash into a new one
# Includes the current commit
squash_amount = 3
seperator = "# # # # # # # # # # # # # # #"


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
    print("Aww yeah!")

    git('fetch', 'origin')
    '''commitsee = git('rev-list', '--left-right', '--reverse', 'HEAD...{0}'.format("yeetus"))

    # first_commit_on_branch = iter(commit for commit in commits if commit.startswith('<'))[1:]
    first_commit_on_branch = ""
    for commit in commitsee:
        if commit.startswith('<'):
            first_commit_on_branch = commit'''

    '''
    relation = 'HEAD'
    # this loop gets and prints every commit message
    times_back = 0
    while not times_back >= squash_amount - 1:
        try:
            # printing this commit gives a long hashy-hash
            commit = git('rev-parse', relation)[0]
            commit_msg = str(git('show', '--no-patch', '--format=%B', commit)[0])
            print("# # # # # # # # # # # # # # #\n" + commit_msg + "\n# # # # # # # # # # # # # # #\n")
        except Exception as e:
            print('Exceptione: ' + str(e))
            break
        times_back += 1
        relation = 'HEAD~' + str(times_back)
        '''

    # TODO: If the branches of commits and their hashes are important for the user to see, move these "messages" to
    #  where they must be used. Don't print them here either, instead just print the results of this log command....

    # Get the commits requested for squashing
    # If squash_amount is higher than the amount of what's available, it'll just get everything
    commits = git('log', '--graph', '--decorate', '--oneline')[:squash_amount]
    # Make a list of their messages
    messages = []
    for c in commits:
        message = git('show', '--no-patch', '--format=%B', c[2:9])[0]
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
    # TODO: If there are no new changes to add (and the commit won't be new), these two will cancel themselves
    #  Maybe also don't add EVERYTHING? Right now it just helps ensure the commit is new
    git('add', '.')
    git('commit', '-m', new_mes)

    # Sleep for one second to give time for the commit to go through
    sleep(1)

    # The commits list doesn't include the newest commit- now it's purely commits to delete
    for c in commits:
        SHA = c[2:9]
        print(SHA)
        git('rebase', '--rebase-merges', '--onto', SHA + '^', SHA)


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

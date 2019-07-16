import sys
from subprocess import Popen, STDOUT, PIPE

# The amount of commits to squash into the current one
squash_amount = 2
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
    commits = git('rev-list', '--left-right', '--reverse', 'HEAD...{0}'.format("yeetus"))

    # first_commit_on_branch = iter(commit for commit in commits if commit.startswith('<'))[1:]
    first_commit_on_branch = ""
    for commit in commits:
        if commit.startswith('<'):
            first_commit_on_branch = commit

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

    thingymabob = git('log', '--graph', '--decorate', '--oneline')[1:squash_amount+1]
    print(seperator)
    print("Commit Messages (new to old):")
    print(seperator)
    messages = []
    for thing in thingymabob:
        messages.append(thing[10:])
        print(thing[10:])

    print(seperator)
    new_mes = ""
    write_new = input("Write a completely new message for the squashed commit? (y/n) ").lower()
    if 'y' == write_new:
        new_mes = input("Write new message below, enter to submit\n")
        print("Cool, thanks...\n" + new_mes)

    elif 'n' == write_new:
        write_new = input("Use latest message? (y) Will combine all messages otherwise ").lower()
        # Combine messages
        if 'y' == write_new:
            # TODO: I don't think this works at all
            print("Combining messages...")
            for m in messages:
                new_mes += m

        # Use latest
        else:
            print("Using latest message")
            # TODO: I don't think this works either
            new_mes = git('log', '--graph', '--decorate', '--oneline')[0][10:]

    else:
        print("Input not accepted, cancelling squish")
        quit()

    print(seperator)
    print("Squashed commit message:")
    print(seperator)
    print(new_mes)

    # [2:9] is the part with the hash
    # print(thingymabob[0][2:9])

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
    '''boop = git('rev-parse', 'HEAD')[0]
    msg_of_first_commit = '\n'.join(git('show', '--no-patch', '--format=%B', boop))
    print(msg_of_first_commit)'''


if __name__ == "__main__":
    main()

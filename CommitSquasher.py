import sys
from subprocess import Popen, STDOUT, PIPE

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
    '''for commitithink in commits:
        print(git('show', '--no-patch', '--format=%B', commitithink))'''

    # first_commit_on_branch = iter(commit for commit in commits if commit.startswith('<'))[1:]
    first_commit_on_branch = ""
    for commit in commits:
        if commit.startswith('<'):
            first_commit_on_branch = commit

    relation = 'HEAD'
    # this loop gets and prints every commit message
    while True:
        try:
            commit = git('rev-parse', relation)[0]
            commit_msg = str(git('show', '--no-patch', '--format=%B', commit)[0])
            print("# # # # # # # # # # # # # # #\n" + commit_msg + "\n# # # # # # # # # # # # # # #\n")
        except Exception as e:
            print('Exceptione: ' + str(e))
            break
        # TODO: maybe get this to use the "~n" format (it might help a bit with storing the number of the commit)
        relation += '^'

    # git branch -f master HEAD~3
    # sets the master branch to being at the commit at HEAD~3

    # git log --graph --decorate --oneline
    # gets a list of commits with their SHA hash IDs

    # git rebase -p --onto xsha^ xsha
    # deletes the commit with the hash xsha

    # rev-parse HEAD gets the most recent commit's hash or something
    # change HEAD to something else to get that commit's has or whatever
    '''boop = git('rev-parse', 'HEAD')[0]
    msg_of_first_commit = '\n'.join(git('show', '--no-patch', '--format=%B', boop))
    print(msg_of_first_commit)'''


if __name__ == "__main__":
    main()

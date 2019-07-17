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
    git('rebase', '-s', '--onto', '92813^', '92813')


if __name__ == "__main__":
    main()
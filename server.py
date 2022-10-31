import os
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'


def conv_dict(ls, delim):
    # converts ls into a dictionary, splitting by delim
    dic = {}
    for i in range(len(ls)):
        ls[i] = ls[i].split(delim)
        dic[ls[i][0]] = ls[i][1]
    return dic


def server():
    pass


def main():
    # TODO
    # prepare for any incoming client connection
    # receive emails from a client and save to disk
    # additionally allow client authentication
    # allow multiple clients to connect simultaniously
    # terminate upon receiving a SIGNT signal
    conf = sys.argv[1]
    with open(conf) as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    conf = conv_dict(lines, '=')


if __name__ == '__main__':
    main()

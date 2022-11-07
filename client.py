import hashlib
import os
import re
import secrets
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAfilename = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'
PERSONAL_SECRET_MD5 = hashlib.md5(PERSONAL_SECRET.encode())
# print(PERSONAL_SECRET_MD5.digest())


def mail(HOST, PORT, to_send):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((HOST, int(PORT)))
    except ConnectionRefusedError:
        print("C: Cannot establish connection")
        sys.exit(3)
    # s.listen()
    # conn, addr = s.accept()

    # Receive the first message from the server
    data = s.recv(1024).decode()
    print(f"S: {data}", end='')
    data = data.split(' ')

    # Send messages while there is no terminate (221) code
    i = 0
    while data[0] != '221':
        # TODO implement a wait for server response, and check
        # server code

        # prints the client output to server in stdout
        print(f"C: {to_send[i]}\r\n", end='')

        # Send to server
        s.send((to_send[i]+"\r\n").encode("ascii", "ignore"))

        # Waits for server response
        data = s.recv(1024).decode()

        # Prints server response
        print(f"S: {data}", end='')

        # Do logic with data
        data = data.split(' ')
        i += 1

    s.close()


def merge_mail(ls1, ls2):
    # merges 2 lists of the formated mail contents and the output
    # to be sent to the server
    ls1[4] = ls2[2:]

    ls = ls1

    # TODO
    # get to: emails
    send = re.findall("<.*?>", ls2[0])
    to = re.findall("<.*?>", ls2[1])

    ls[1] = ["MAIL FROM:"+send[0]]
    for i in range(len(to)):
        ls[2].append("RCPT TO:"+to[i])

    ls = [item for sublist in ls for item in sublist]

    return ls


def parse_mail(file, host):
    # reads a file and returns a list of line by line to send information
    # to server
    ls = [[f"EHLO {host}"],
          [],
          [],
          ["DATA"],
          [],
          ["."],
          ["QUIT"]]

    with open(file) as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    ls = merge_mail(ls, lines)

    return ls


def conv_dict(ls, delim):
    # converts ls into a dictionary, splitting by delim
    dic = {}
    for i in range(len(ls)):
        ls[i] = ls[i].split(delim)
        dic[ls[i][0]] = ls[i][1]
    return dic


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    conf = sys.argv[1]
    if not os.path.isfile(conf):
        sys.exit(2)

    with open(conf) as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    conf = conv_dict(lines, '=')

    # use the conf file to get relevant information
    try:
        send_path = conf['send_path']
        port = conf['server_port']
    except KeyError:
        sys.exit(2)

    host = "127.0.0.1"

    to_send = []

    # Werid stuff to work work locally/remotely
    # absolute_path = os.path.dirname(__file__)
    # send_path = absolute_path+send_path
    if not os.path.isdir(send_path):
        print("unreadable send path")
        sys.exit(2)

    for filename in os.listdir(send_path):
        path = os.path.join(send_path, filename)
        path = path
        if os.path.isfile(path):
            to_send.append(parse_mail(path, host))

    for i in range(len(to_send)):
        if False:
            pass
        else:
            path = os.path.abspath(path)
            print(f"C: {path}: Bad formation")
            sys.exit(0)
        mail(host, port, to_send[i])


if __name__ == '__main__':
    main()

import os
import socket
import sys
import re


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'


def mail(HOST, PORT, to_send):

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, int(PORT)))
            # s.listen()
            # conn, addr = s.accept()

            # check for 220 code

            for i in range(len(to_send)+1):
                # TODO implement a wait for server response, and check
                # server code

                # Waits for server response
                data = s.recv(1024).decode()
                # Prints server response
                print(f"S: {data}", end='')

                # Do logic with data
                data = data.split(' ')
                print("data:",data[0])
                if data[0] == "221":
                    s.close()

                # prints the client output to server in stdout
                print(f"C: {to_send[i]}\r\n", end='')
                # Send to server
                s.send((to_send[i]+"\r\n").encode("ascii", "ignore"))
    except ConnectionRefusedError:
        print("no server")
        sys.exit(3)


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


def parse_mail(file):
    # reads a file and returns a list of line by line to send information
    # to server
    ls = [["EHLO 127.0.0.1"],
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
        print("no conf supplied")
        sys.exit(1)

    conf = sys.argv[1]
    if not os.path.isfile(conf):
        print("invalid conf file")
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
        print("incomplete conf")
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
            to_send.append(parse_mail(path))
        else:
            print("")

    for i in range(len(to_send)):
        mail(host, port, to_send[i])


if __name__ == '__main__':
    main()

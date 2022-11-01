import os
import socket
import sys
import re


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'


def mail(HOST, PORT, to_send):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, int(PORT)))
        # s.listen()
        # conn, addr = s.accept()

        for i in range(len(to_send)):
            s.send((to_send[i]+'\n').encode())


def merge_mail(ls1, ls2):
    # merges 2 lists of the formated mail contents and the output
    # to be sent to the server
    ls1[4] = ls2[2:]

    ls = ls1
    # print(ls2)

    # TODO
    # get to: emails
    send = re.findall("<.*?>", ls2[0])
    to = re.findall("<.*?>", ls2[1])

    # print(ls)
    ls[1] = ["MAIL FROM:"+send[0]]
    for i in range(len(to)):
        ls[2].append("MAIL TO:"+to[i])

    ls = [item for sublist in ls for item in sublist]

    return ls


def parse_mail(file):
    # reads a file and returns a list of line by line to send information
    # to server
    ls = [["ELHO"],
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


def connect():
    # TODO
    # 1. Create a socket
    # 2. Connect to the server
    # 3. Send the personal ID and secret to the server
    # 4. Receive the response from the server
    # 5. Print the response
    # 6. Close the socket
    pass


def main():
    if len(sys.argv) != 2:
        print("no conf supplied")
        sys.exit("exit code 1")

    conf = sys.argv[1]
    if not os.path.isfile(conf):
        print("invalid conf file")
        sys.exit("exit code 2")

    with open(conf) as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    # print(f"c: {lines}")

    conf = conv_dict(lines, '=')
    print(conf)

    # use the conf file to get relevant information
    send_path = conf['send_path']
    port = conf['server_port']
    host = "127.0.0.1"

    to_send = []
    
    for filename in os.listdir(send_path[1:]):
        path = os.path.join(send_path[1:], filename)
        print(path)
        if os.path.isfile(path):
            to_send.append(parse_mail(path))
    # parse_mail(send_path)

    print(*to_send, sep='\n\n')

    for i in range(len(to_send)):
        mail(host, port, to_send[i])


if __name__ == '__main__':
    main()

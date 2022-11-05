import hashlib
import os
import re
import secrets
import socket
import sys


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'

# -- Generate random challenge -- #
# challenge = secrets.token_urlsafe(16)
# print("challenge:", challenge)


def log_data(file, data):
    pass


def conv_dict(ls, delim):
    # converts ls into a dictionary, splitting by delim
    dic = {}
    for i in range(len(ls)):
        ls[i] = ls[i].split(delim)
        dic[ls[i][0]] = ls[i][1]
    return dic


def server_response(data, checkpoints, rcpt_check):
    # Returns a tuple of (response, updated_checkpoints, rcpt_check)
    code_220 = "220 Service ready"
    code_221 = "221 Service closing transmission channel"
    code_235 = "235 Authentication succeeded"
    code_250 = "250 Requested mail action okay, completed"
    code_334 = "334 Server BASE64-encoded challenge"
    code_354 = "354 Start mail input; end with <CRLF>.<CRLF>"
    code_421 = "421 Service not available, closing transmission channel"

    code_500 = "500 Syntax error, command unrecognized"
    code_501 = "501 Syntax error in parameters or arguments"
    code_503 = "503 Bad sequence of commands"
    code_504 = "504 Command parameter not implemented"
    code_535 = "535 Authentication credentials invalid"

    response = code_500

    commands = ['EHLO', 'MAIL', 'RCPT', 'DATA', 'RSET', 'NOOP', 'AUTH', 'QUIT']

    if data[0] not in commands:
        response = code_500

    # Use the checkpoints to determine where it is up to

    if data[0] == 'RSET':
        if len(data) == 1:
            checkpoints = dict.fromkeys(checkpoints, False)
        else:
            response = code_501

    # print(data)

    # check EHLO
    if data[0] == 'EHLO':
        # might have to check for a valid ipv4 address
        # but this works for now
        if data[1] == '127.0.0.1':
            response = f"250 {data[1]}\r\nS: 250 AUTH CRAM-MD5"
            checkpoints['EHLO'] = True
        else:
            response = "501 Syntax error in parameters or arguments"

    # check MAIL FROM:
    if checkpoints['EHLO'] is True:
        if data[0] == 'MAIL':
            # TODO check for a valid email address
            # if data[2] == valid email address
            if len(data) == 2:
                response = code_250
                checkpoints['MAIL'] = True
            else:
                response = code_501

    # check RCPT TO:
    if checkpoints['MAIL'] is True:
        if data[0] == 'RCPT':

            # # TODO check for a valid email address
            # if data[2] == valid email address
            if len(data) == 2:
                response = code_250
                rcpt_check = True
            else:
                response = code_501

    # check DATA:
    if data[0] == 'DATA' and rcpt_check is True:
        if len(data) == 1:
            response = code_354
            checkpoints['RCPT'] = True
            checkpoints['DATA'] = True
        else:
            response = code_501

    if checkpoints['DATA'] is True and checkpoints['RCPT'] is True:
        if data[0] == '.':
            response = "250 Requested mail action okay completed"
            checkpoints['.'] = True
        if checkpoints['.'] is True:
            if data[0] == 'QUIT':
                response = code_221
                checkpoints['QUIT'] = True
        else:
            response = code_354

    # check .:

    # check QUIT:
    if data[0] == 'QUIT':
        response = "221 Service closing transmission channel"

    # print(checkpoints)

    return (response, checkpoints, rcpt_check)


def server(HOST, PORT, checkpoints):
    rcpt_check = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            # Connection established
            print("S: 220 Service ready\r\n", end='', flush=True)
            conn.send("220 Service ready\r\n".encode())

            # authentication

            # Mesasge loop
            while True:
                # Receive client message
                data = conn.recv(1024).decode()

                # If no client says nothing, do nothing
                if not data:
                    continue

                # Print out client message
                print(f"C: {data}", end='', flush=True)

                # Server response
                # do logic with data check if appropriate
                # response and formulate send code

                # print("\\n ", data[-1] == '\n')
                # print("\\r ", data[-2] == '\r')
                # check if client msg contains \r\n and data[-3] is alpha
                if not data[-3].isalnum() or data[-2]=='\r' or data[-1]=='\n':
                    response = "501 Syntax error in parameters or arguments"
                    print(f"S: {response}\r\n", end='', flush=True)
                    conn.send((response+'\r\n').encode())
                    data = data.strip()
                    print(f"C: {data}\r\n", end='', flush=True)
                    continue
                data = data.strip()
                data = data.split()
                if data[0] == "QUIT":
                    response = "221 Service closing transmission channel"
                    print(f"S: {response}\r\n", end='', flush=True)
                    conn.send((response+'\r\n').encode())
                    continue
                response, checkpoints, rcpt_check = server_response(data, checkpoints, rcpt_check)

                # Check authentication
                if checkpoints['EHLO'] is True and checkpoints['MAIL'] is False:
                    pass

                # print(response)
                # print(checkpoints)
                print(f"S: {response}\r\n", end='')

                conn.send((response+'\r\n').encode())


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

    conf = conv_dict(lines, '=')

    host = "127.0.0.1"
    port = int(conf["server_port"])
    write_path = conf['inbox_path']

    checkpoints = {'EHLO': False,
                   'MAIL': False,
                   'RCPT': False,
                   'DATA': False,
                   '.': False,
                   'QUIT': False}

    server(host, port, checkpoints)


if __name__ == '__main__':
    main()

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


def server(HOST, PORT, checkpoints):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            # Connection established
            print("S: 220 Service ready\r\n", end='')
            conn.send("220 Service ready\r\n".encode())

            # authentication

            # Mesasge loop
            while True:
                # Receive client message
                data = conn.recv(1024).decode()
                data = data.strip()

                # If no client says nothing, do nothing
                if not data:
                    continue

                # Print out client message
                print(f"C: {data}\r\n", end='', flush=True)

                data = data.split(' ')

                # Server response
                # do logic with data
                if data[0] == "QUIT":
                    response = "221 Service closing transmission channel"
                    print(f"S: {response}\r\n", end='')
                    conn.send((response+'\r\n').encode())
                    s.close()
                elif data[0] == "ELHO":
                    if (len(data) == 2):
                        if data[1] == HOST:
                            response = "250 " + HOST
                        else:
                            response = "501 Syntax error in parameters or arguments"
                elif data[0] == 'MAIL' or data[0] == 'RCPT':
                    response = "250 Requested mail action"
                else:
                    response = "221"
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

    checkpoints = {'EHLO': False,
                   'MAIL FROM': False,
                   'RCPT TO': False,
                   'DATA': False,
                   '.': False,
                   'QUIT': False}

    test = [False, False, False, False, False, False]

    server(host, port, checkpoints)


if __name__ == '__main__':
    main()

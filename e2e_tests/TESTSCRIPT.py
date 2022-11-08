import socket
import sys


############################
# SCRIPT TO GENERATE TESTS #
############################


def main():
    if len(sys.argv) != 2:
        print("no file")
        sys.exit()

    file = sys.argv[1]

    HOST = '127.0.0.1'
    PORT = 2010

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, int(PORT)))

    with open(file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        data = s.recv(1024).decode()
        line = line.strip()
        s.send((line+'\r\n').encode())

    s.close()


if __name__ == "__main__":
    main()

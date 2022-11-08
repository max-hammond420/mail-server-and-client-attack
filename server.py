from datetime import datetime
import base64
import hmac
import hashlib
import os
import random
import re
import secrets
import socket
import sys
import time


# Visit https://edstem.org/au/courses/8961/lessons/26522/slides/196175 to get
PERSONAL_ID = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'

# -- Generate random challenge -- #
# challenge = secrets.token_urlsafe(16)
# print("challenge:", challenge)


def parse_complete_email_to_log(data):
    # takes in a list of the completed email and
    # returns a list of each line to output in the file
    base = ["From: ",
            "To: "]

    for i in range(len(data)):
        if data[i].startswith("MAIL FROM:"):
            email = re.findall("<.*?>", data[i])
            base[0] += email[0]
        if data[i].startswith("RCPT TO:"):
            emails = re.findall("<.*?>", data[i])
            for email in emails:
                base[1] += email+','
        if data[i].startswith("Date:"):
            while data[i] != '.\r\n':
                base.append(data[i].strip())
                i += 1
            break

    base[1] = base[1][:-1]
    return base


def convert_to_unixtime(date):
    # takes in date in rfc form and converts it to unix time

    date = re.sub(r'[^\w\s]', '', date)
    date = date.split(' ')

    hour = int(date[4][:2])
    minute = int(date[4][2:4])
    seconds = int(date[4][4:6])
    day = int(date[1])
    month = date[2]
    year = int(date[3])

    month = datetime.strptime(month, '%b').month
    # print(date)
    # print(year, month, day, hour, minute)
    date_time = datetime(year, month, day, hour, minute, seconds)
    unixtime = int(time.mktime(date_time.timetuple()))
    return unixtime

    # print(day, month, year, hour)


def log_data(file, data):
    # get date in unix time
    for i in range(len(data)):
        if data[i].startswith('Date'):
            new_date = data[i]
            new_date = new_date.split(':', 1)
            new_date[1] = new_date[1].strip()
            timestamp = convert_to_unixtime(new_date[1])

    filename = file+'/'+str(timestamp)+'.txt'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, 'w')
    to_log_data = parse_complete_email_to_log(data)
    for line in to_log_data:
        f.write(line+'\n')
    f.close()


def conv_dict(ls, delim):
    # converts ls into a dictionary, splitting by delim
    dic = {}
    for i in range(len(ls)):
        ls[i] = ls[i].split(delim)
        dic[ls[i][0]] = ls[i][1]
    return dic


def compute_digest(challenge):
    # computets the digest that is supposed to come from the client
    base64_bytes = challenge.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    PERSONAL_SECRET_MD5 = hmac.new(PERSONAL_SECRET.encode(), message_bytes, hashlib.md5).hexdigest()
    to_send = PERSONAL_ID + ' ' + PERSONAL_SECRET_MD5
    to_send = to_send.encode('ascii')
    base64_bytes = base64.b64encode(to_send)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def generate_challenge():
    # returns a string that is 16 <= len <= 128 bytes
    bytes = random.randint(16, 128)
    challenge = secrets.token_hex(bytes)
    challenge = challenge.encode('ascii')
    base64_bytes = base64.b64encode(challenge)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def check_ipv4(ip):
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False
        return ip.count('.') == 3
    except socket.error:
        return False

    return True


def check_email(prefix, data):
    # Checks if email is the form of prefix:<email>
    # returns a tuple of (bool, email)
    # email is none if bool is false

    is_valid = False
    email = None
    data = data.split(':')

    let_dig = 'a-zA-Z0-9'
    ldh_str = f'[{let_dig}-]*[{let_dig}]'
    atom = f'[{let_dig}][{let_dig}-]*'
    dot_string = fr'{atom}(.{atom})*'

    sub_domain = f'[{let_dig}]+({ldh_str})'
    domain = rf'{sub_domain}*(\.{sub_domain})+'

    test = re.compile(f"<{dot_string}@{domain}>")

    # should be ['prefix', '<email>']
    if len(data) == 2:
        if data[0] == prefix:
            # if data[1].match
            email = re.search(test, data[1])
            if email:
                is_valid = True

    return (is_valid, email)


def server_response(data, checkpoints, rcpt_check):
    # Returns a tuple of (response, updated_checkpoints, rcpt_check)
    code_220 = "220 Service ready"
    code_221 = "221 Service closing transmission channel"
    code_235 = "235 Authentication succeeded"
    code_250 = "250 Requested mail action okay completed"
    code_334 = "334 Server BASE64-encoded challenge"
    code_354 = "354 Start mail input end <CRLF>.<CRLF>"
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

    if data[0] == 'RSET' and checkpoints['DATA'] is False:
        if len(data) == 1:
            if checkpoints['EHLO'] is True:
                checkpoints = dict.fromkeys(checkpoints, False)
                checkpoints['EHLO'] = True
            else:
                checkpoints = dict.fromkeys(checkpoints, False)
            rcpt_check = False
            response = code_250
        else:
            response = code_501

    # print(data)

    # check NOOP
    if data[0] == 'NOOP':
        if len(data) == 1:
            response = code_250
        else:
            response = code_501

    # check EHLO
    if data[0] == 'EHLO':
        # might have to check for a valid ipv4 address
        # but this works for now
        if len(data) == 2:
            # print("ipv4:", check_ipv4(data[1]))
            if check_ipv4(data[1]):
                response = "250 127.0.0.1\r\n250 AUTH CRAM-MD5"
                checkpoints['EHLO'] = True
            else:
                response = code_501
        else:
            response = code_501
    # check MAIL FROM:
    if data[0] == 'MAIL':
        if checkpoints['EHLO'] is True and checkpoints['MAIL'] is False:
            # TODO check for a valid email address
            # if data[2] == valid email address
            if len(data) == 2:
                valid, mail_email = check_email('FROM', data[1])
                if valid:
                    response = code_250
                    checkpoints['MAIL'] = True
                else:
                    response = code_501
            else:
                response = code_501
        else:
            response = code_503

    # check RCPT TO:
    if data[0] == 'RCPT':
        if checkpoints['MAIL'] is True and checkpoints['RCPT'] is False:

            # TODO check for a valid email address
            # if data[2] == valid email address
            if len(data) == 2:
                valid, rcpt_email = check_email('TO', data[1])
                if valid:
                    response = code_250
                    rcpt_check = True
                else:
                    response = code_501
            else:
                response = code_501
        else:
            response = code_503

    # check DATA:
    if data[0] == 'DATA':
        if rcpt_check is True:
            if len(data) == 1:
                response = code_354
                checkpoints['RCPT'] = True
                checkpoints['DATA'] = True
            else:
                response = code_501
        else:
            response = code_503

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

    return (response, checkpoints, rcpt_check)


def server(HOST, PORT, checkpoints, file):
    ls = []
    rcpt_check = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            # Connection established
            print("S: 220 Service ready\r\n", end='', flush=True)
            conn.send("220 Service ready\r\n".encode())

            # Mesasge loop
            while True:
                # Receive client message
                data = conn.recv(1024).decode()

                # AUTH
                if data == "AUTH CRAM-MD5\r\n":
                    challenge = generate_challenge()
                    response = f"334 {challenge}"
                    # print(response)
                    print(f"S: {response}\r\n", end='', flush=True)
                    conn.send((response+'\r\n').encode())
                    data = conn.recv(1024).decode()
                    decoded_response = base64.b64decode(data)
                    a = compute_digest(challenge)
                    print(decoded_response)
                    print(a)

                # If no client says nothing, do nothing
                if not data:
                    continue

                # Print out client message
                print(f"C: {data}", end='', flush=True)

                # Server response
                # do logic with data check if appropriate
                # response and formulate send code

                if data[-3].isspace() or data[-2] != '\r' or data[-1] != '\n':
                    response = "501 Syntax error in parameters or arguments"
                    print(f"S: {response}\r\n", end='', flush=True)
                    conn.send((response+'\r\n').encode())
                    continue

                ls.append(data)

                data = data.strip()
                data = data.split()

                if data[0] == "QUIT":
                    response = "221 Service closing transmission channel"
                    print(f"S: {response}\r\n", end='', flush=True)
                    conn.send((response+'\r\n').encode())

                    # Log the data
                    for i in range(len(ls)):
                        if ls[i].startswith("Date: "):
                            log_data(file, ls)
                            break
                    continue

                response, checkpoints, rcpt_check = server_response(data, checkpoints, rcpt_check)
                # print(f"{data[0]}, {response}", flush=True)
                if response[:3] == '500' and (data[0].startswith('RCPT') or data[0].startswith('MAIL')):
                    response = '501 Syntax error in parameters or arguments'

                conn.send((response+'\r\n').encode())

                if '\r\n' in response:
                    response = response.split('\r\n')
                    print(f"S: {response[0]}\r\nS: {response[1]}\r\n", end='', flush=True)
                else:
                    print(f"S: {response}\r\n", end='', flush=True)


def main():
    if len(sys.argv) != 2:
        print("no conf supplied, server")
        sys.exit(1)

    conf = sys.argv[1]
    if not os.path.isfile(conf):
        print("invalid conf file, server")
        sys.exit(2)

    with open(conf) as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    conf = conv_dict(lines, '=')

    try:
        inbox_path = conf['inbox_path']
        port = int(conf['server_port'])
    except KeyError:
        print("incomplete conf, server")
        sys.exit(2)

    host = "127.0.0.1"

    checkpoints = {'EHLO': False,
                   'MAIL': False,
                   'RCPT': False,
                   'DATA': False,
                   '.': False,
                   'QUIT': False}

    try:
        server(host, port, checkpoints, inbox_path)
    except KeyboardInterrupt:
        print("\nS: SIGINT received, closing\r\n", end='', flush=True)
        sys.exit()


if __name__ == '__main__':
    main()

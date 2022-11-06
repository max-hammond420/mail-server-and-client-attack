import socket
import re


def valid_ipv4(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


def check_email(prefix, data):
    # Checks if email is the form of prefix:<email>
    # returns a tuple of (bool, email)
    # email is none if bool is false

    is_valid = False
    email = None
    data = data.split(':')

    # let_dig = fr'[a-zA-Z0-9]'
    # ldh_str = fr'({let_dig}|-) {let_dig}'
    # atom = fr'{let_dig} *({let_dig}|-)'
    # dot_string = fr'{atom} *(.{atom})'
    # sub_domain = fr'let_dig [{ldh_str}]'
    # domain = fr'{sub_domain} +(.{sub_domain})'
    # mailbox = fr'<{dot_string}@{domain}>'
    # email_regex = re.compile(mailbox)

    # let_dig = "a-zA-Z0-9"

    # atom = f"[{let_dig}][{let_dig}-]*"
    # dot_string = f"[{atom}][.{atom}]*"
    # mailbox = f"{dot_string}@{domain}"

    let_dig = 'a-zA-Z0-9'
    # ldh_str = f"[{let_dig}-]*{let_dig}"
    atom = f'[{let_dig}][{let_dig}-]*'
    dot_string = f'{atom}[.{atom}]*'

    # sub_domain = f"[{let_dig}][{let_dig}-]"
    domain = fr'{atom}[.{atom}]*'

    # test = f'<{dot_string}@{domain}>'
    test = fr'([A-Za-z0-9]+[.-])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    # should be ['prefix', '<email>']
    if len(data) == 2:
        if data[0] == prefix:
            # if data[1].match
            email = re.search(regex, data[1])
            if email:
                is_valid = True

    return (is_valid, email)


print(check_email('TO', 'TO:<asdf@asdf.org>'))
print(check_email('TO', 'TO:<bob@bob.org>'))
print(check_email('TO', 'TO:<bob@bob.org.org.org>'))
print(check_email('TO', 'TO: <bob@bob.org'))
print(check_email('TO', 'TO:<bob@boborg>'))

import re


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
    ldh_str = f"[a-zA-Z0-9-]*[{let_dig}]"
    atom = f'[{let_dig}][{let_dig}-]*'
    dot_string = f'{atom}[.{atom}]*'

    sub_domain = f"[{let_dig}]*"
    domain = f"[{let_dig}][.{let_dig}]+"

    test = f'<{dot_string}@{domain}>'

    # should be ['prefix', '<email>']
    if len(data) == 2:
        if data[0] == prefix:
            # if data[1].match
            email = re.search(test, data[1])
            if email:
                is_valid = True

    return (is_valid, email)


print(check_email("TO", "TO:<asdf@asfd.com>"))
print(check_email("TO", "TO:<as.df@asfd.com>"))
print(check_email("TO", "TO:asdfasdf@asdf"))

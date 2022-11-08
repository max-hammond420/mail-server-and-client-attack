import secrets
import hashlib
import base64
import random


PERSONAL_ID = 'F8D819'
PERSONAL_SECRET = '44c42ab54ed4c444130f09261509f85b'


def generate_challenge():
    # returns a string that is 16 <= len <= 128 bytes
    bytes = random.randint(16, 128)
    challenge = secrets.token_hex(bytes)
    challenge = challenge.encode('ascii')
    base64_bytes = base64.b64encode(challenge)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def compute_digest(challenge):
    # computets the digest that is supposed to come from the client
    base64_bytes = challenge.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    if isinstance(message_bytes, bytes):
        print('bytes')
    elif isinstance(message_bytes, str):
        print('str')
    else:
        print("asdf")
    PERSONAL_SECRET_MD5 = hashlib.md5(message_bytes).hexdigest()
    to_send = PERSONAL_ID + PERSONAL_SECRET_MD5
    to_send = to_send.encode('ascii')
    base64_bytes = base64.b64encode(to_send)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


# a = generate_challenge()
a = 'NWUxYzc2MzJhNTAzODMzZWQxODhkNWZiNWYwMTA2OWQ2ZjVmNmJiYTY5M2NkYTJhNzZhMDNiNWM1ZmI3NWI='
print(a)

b = compute_digest(a)
print(b)

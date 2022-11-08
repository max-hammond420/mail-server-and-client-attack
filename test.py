import secrets
import random
import base64


def generate_challenge():
    # returns a string that is 16 <= len <= 128 bytes
    bytes = random.randint(16, 128)
    challenge = secrets.token_hex(bytes)
    challenge = challenge.encode('ascii')
    base64_bytes = base64.b64encode(challenge)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


a = generate_challenge()
print(a)

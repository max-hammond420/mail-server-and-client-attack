import secrets
import random


def generate_challenge():
    # returns a string that is 16 <= len <= 128 bytes
    bytes = random.randint(16, 128)
    challenge = secrets.token_hex(bytes)
    return challenge


a = generate_challenge()
print(a)

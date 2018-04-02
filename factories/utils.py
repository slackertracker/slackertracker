import random, string

def generate_id(first=None):
    if not first:
        first = random.choice(string.ascii_uppercase)

    return first[0].upper() + ''.join(random.choices(string.digits, k=7))

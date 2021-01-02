import string
import random


def generate_pass(pass_length):
    letters = string.ascii_letters
    numbers = string.digits

    passable = list(f'{letters}{numbers}')
    random.shuffle(passable)

    random_password = random.choices(passable, k=pass_length)
    random_password[0] = '?' if random_password[0] == '/' else random_password[0]
    random_password = ''.join(random_password)

    return random_password

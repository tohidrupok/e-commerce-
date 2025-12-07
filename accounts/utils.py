import random
import string

def generate_username_from_phone(phone):
    # sanitize phone to allowed username characters
    clean = "".join(ch for ch in phone if ch.isdigit())
    if not clean:
        clean = "".join(random.choice(string.digits) for _ in range(8))
    return f"user_{clean}"

def generate_unique_username(user_model, base_username):
    username = base_username
    suffix = 0
    while user_model.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base_username}_{suffix}"
    return username

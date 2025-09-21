import secrets
import string

def generate_password(length=28):
    characters = string.ascii_letters + string.punctuation + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

if __name__ == "__main__":
    password = generate_password()
    print("Your generated password:")
    print(password)



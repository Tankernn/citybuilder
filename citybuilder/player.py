from passlib.hash import pbkdf2_sha256

class Player:
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)


    def set_password(self, password):
        self.password = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def update(self):
        pass

import math
import random

class PasswordEncryption:
    def __init__(self, identifier):
        self.identifier = identifier
        self.x = self.generate_radom_x()
        self.y = self.calculate_fn()

    def generate_radom_x(self):
        return round(random.random(), 4)

    def calculate_fn(self):
        return round(self.x / math.sin(self.identifier), 4)

    def getEncryptedId(self):
        return self.y;
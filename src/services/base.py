import json


class EmailExists(Exception):

    def __init__(self, email):
        self.email = email

    def json(self):
        return json.dumps(
            {
                'message': 'email already exists.',
                'email': self.email
            }
        )


class WrongPassword(Exception):

    def __init__(self, password: str):
        self.password = password

    def json(self):
        return json.dumps(
            {
                'message': 'Wrong password.',
                'email': self.password
            }
        )
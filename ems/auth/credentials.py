
import getpass

from ems.auth import CredentialsBroker

class PlainPasswordBroker(CredentialsBroker):

    def validate(self, user, **credentials):
        return (user.password == credentials['password'])

class AlwaysTrueBroker(CredentialsBroker):

    def __init__(self, loginAs='admin'):
        self.loginAs = loginAs

    def validate(self, user, **credentials):
        return True

    def translate(self, **credentials):
        if self.loginAs:
            credentials['username'] = self.loginAs
        return credentials

class GetPassBroker(CredentialsBroker):

    def translate(self, **credentials):
        credentials['username'] = getpass.getuser()
        return credentials

    def validate(self, user, **credentials):
        return (user.name == getpass.getuser())

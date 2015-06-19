
import getpass

from ems.typehint import accepts
from ems.auth import UserContainer, UserProvider, UserNotFoundError

class FixedUserNameContainer(UserContainer):

    @accepts(UserProvider)
    def __init__(self, userProvider):
        self._provider = userProvider
        self._userName = 'admin'

    @property
    def userName(self):
        return self._userName

    @userName.setter
    def setUserName(self, userName):
        self._userName = userName

    def get(self):

        if self.user:
            return self.user

        credentials = {'username': self.userName}

        try:
            self.user = self._provider.findByCredentials(**credentials)
        except UserNotFoundError:
            pass

        return self.user


    def set(self, user, persist=False):
        self.user = user

    def clear(self):
        self.user = None

class GetPassContainer(FixedUserNameContainer):

    @property
    def userName(self):
        return getpass.getuser()

    @userName.setter
    def setUserName(self, userName):
        raise NotImplementedError('GetPassContainer doesnt support manual username')
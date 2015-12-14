
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSlot


from ems.auth import Authentication, User, AuthGroup

class QAuth(QObject):

    def __init__(self, baseAuth):
        self._baseAuth = baseAuth
        self._qUser = None
        super().__init__()

    def getUser(self):

        baseUser = self._baseAuth.user

        if self._qUser is not None and self._qUser.id == baseUser.user.id:
            return self._qUser

        self._qUser = QUser(baseUser)

        return self._qUser

    user = pyqtProperty(QUser, getUser)

    @pyqtSlot(bool)
    def isAuthenticated(self):
        return self._baseAuth.isAuthenticated

    @pyqtSlot("QVariantMap")
    def login(self, credentials):
        return self._baseAuth.login(**credentials)

    @pyqtSlot()
    def logout(self):
        self._baseAuth.logout()


class QUser(QObject):

    def __init__(self, baseUser):
        super().__init__()
        self._baseUser = baseUser

    def getId(self):
        return self._baseUser.id

    id = pyqtProperty(int, getId)

    def getPassword(self):
        return self._baseUser.password

    password = pyqtProperty(str, getPassword)

    def getName(self):
        return self._baseUser.name

    name = pyqtProperty(str, getName)
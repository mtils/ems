
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSlot, pyqtSignal


from ems.auth import Authentication, User, AuthGroup, AuthenticatedUser


class QUserProxy(QObject):

    idChanged = pyqtSignal(int)
    nameChanged = pyqtSignal(str)
    passwordChanged = pyqtSignal(str)

    def __init__(self, baseUser=None):
        super().__init__()
        self._baseUser = baseUser
        self._id = -1
        self._name = ''
        self._password = ''

    def getId(self):
        return self._id

    def _setId(self, id_):
        if self._id == id_:
            return
        self._id = id_
        self.idChanged.emit(self._id)

    id = pyqtProperty(int, getId, notify=idChanged)

    def getPassword(self):
        return self._password

    def _setPassword(self, password):
        if self._password == password:
            return
        self._password = password
        self.passwordChanged.emit(self._password)

    password = pyqtProperty(str, getPassword, notify=passwordChanged)

    def getName(self):
        return self._name

    def _setName(self, name):
        if self._name == name:
            return
        self._name = name
        self.nameChanged.emit(self._name)

    name = pyqtProperty(str, getName, notify=nameChanged)

    def _getBaseUser(self):
        return self._baseUser

    def _setBaseUser(self, baseUser):
        self._baseUser = baseUser
        self._setId(self._baseUser.id)
        self._setName(self._baseUser.name)
        self._setPassword(self._baseUser.password)

class QAuthentication(QObject):

    def __init__(self, baseAuth):
        super().__init__()
        self._baseAuth = None
        self._qUser = QUserProxy(self)
        self._setBaseAuth(baseAuth)

    def getUser(self):
        return self._qUser

    user = pyqtProperty(QObject, getUser)

    @pyqtSlot(bool)
    def isAuthenticated(self):
        return self._baseAuth.isAuthenticated

    @pyqtSlot("QVariantMap")
    def login(self, credentials):
        return self._baseAuth.login(**credentials)

    @pyqtSlot()
    def logout(self):
        self._baseAuth.logout()

    def _setBaseUser(self, baseUser):
        self._qUser._setBaseUser(baseUser)

    def _setBaseAuth(self, baseAuth):
        self._baseAuth = baseAuth
        if self._baseAuth.isAuthenticated():
            self._setBaseUser(self._baseAuth.user)

        self._baseAuth.loggedIn += self._setBaseUser

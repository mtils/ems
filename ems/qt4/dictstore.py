
from PyQt4.QtCore import QObject, pyqtSignal, QVariant

class DictStore(QObject):

    valueChanged = pyqtSignal(str,QVariant)
    dirtyStateChanged = pyqtSignal(bool)

    def __init__(self, srcDict, parent=None):
        QObject.__init__(self, parent)
        self._dirty = False
        self.setSrc(srcDict)

    def src(self):
        return self._srcDict

    def setSrc(self, srcDict):
        self._srcDict = srcDict
        self._setDirty(False)

    def isDirty(self):
        return self._dirty

    def _setDirty(self, dirty):
        if dirty != self._dirty:
            self._dirty = dirty
            self.dirtyStateChanged.emit(self._dirty)

    def __getitem__(self, key):
        if '.' in key:
            return DictStore._extractDictValueByList(self._srcDict, key.split('.'))
        else:
            return self._srcDict.__getitem__(key)

    def __setitem__(self, key, value):
        if '.' in key:
            originalValue = DictStore._extractDictValueByList(self._srcDict, key.split('.'))
            if originalValue != value:
                DictStore._setDictValueByList(self._srcDict, key.split('.'), value)
                self.valueChanged.emit(key,QVariant(value))
                self._setDirty(True)
        else:
            try:
                if self._srcDict[key] != value:
                    self._srcDict[key] = value
                    self.valueChanged.emit(key,QVariant(value))
                    self._setDirty(True)
            except KeyError:
                self._srcDict[key] = value
                self.valueChanged.emit(key,QVariant(value))
                self._setDirty(True)

    @staticmethod
    def _extractDictValueByList(srcDict, keyList):
        keyListLen = len(keyList)
        if keyListLen > 0:
            currentTile = keyList[0]
            if currentTile in srcDict:
                val = srcDict[currentTile]
                if keyListLen == 1:
                    return val
                else:
                    keyList.pop(0)
                    return DictStore._extractDictValueByList(val, keyList)

    @staticmethod
    def _setDictValueByList(srcDict, keyList, value):
        keyListLen = len(keyList)
        if keyListLen > 0:
            currentTile = keyList[0]
            if currentTile in srcDict:
                if keyListLen == 1:
                    srcDict[currentTile] = value
                else:
                    keyList.pop(0)
                    return DictStore._setDictValueByList(srcDict[currentTile], keyList, value)

    def __delitem__(self, key):
        self._srcDict.__delitem__(key)



if __name__ == '__main__':

    from ems.qt4.util import SignalPrinter

    testDict = {
        'name': 'Peter',
        'age': 35,
        'job': {
            'name':'Officer',
            'categories':('Police','State')
        }
    }

    s = DictStore(testDict)
    s.emitter = SignalPrinter()
    s.valueChanged.connect(s.emitter.printSignal)
    s.dirtyStateChanged.connect(s.emitter.printSignal)

    for key in ('name','age','job.name','job.categories'):
        print s[key]
    
    print "Dirty?",s.isDirty()
    s['name'] = 'Monalisa'
    s['age'] = 364
    s['job.name'] = 'Model'
    s['job.categories.0'] = 'Fashion'
    print "Dirty?",s.isDirty()
    print s.src()



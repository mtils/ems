#coding=utf-8

from six import u, text_type

from ems.qt import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt
QTextEdit = QtWidgets.QTextEdit
QTextCursor = QtGui.QTextCursor
QCompleter = QtWidgets.QCompleter
QFrame = QtWidgets.QFrame


class CompletionTextEdit(QTextEdit):

    END_OF_WORD = u("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-= \n\r\t")

    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self._completer = None
        self.moveCursor(QTextCursor.End)
        self.minimalCompletionChars = 3
        self._completionTrigger = ''

    def completer(self):
        return self._completer

    def setCompleter(self, completer):
        if self._completer:
            self.disconnect(self._completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.popup().setFrameStyle(QFrame.Plain)
        completer.popup().setFrameShape(QFrame.Box)
        self._completer = completer
        self._completer.activated.connect(self.insertCompletion)

    @property
    def completionTrigger(self):
        return self._completionTrigger

    @completionTrigger.setter
    def completionTrigger(self, triggerChar):
        if self._completionTrigger == triggerChar:
            return
        if self._completionTrigger:
            self.END_OF_WORD = self.END_OF_WORD + self._completionTrigger
        self.END_OF_WORD = self.END_OF_WORD.replace(triggerChar,'')
        self._completionTrigger = triggerChar

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (completion.length() -
            self._completer.completionPrefix().length())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = QTextCursor(self.textCursor())

        currentPos = tc.position()
        startPos = 0

        #tc.select(QTextCursor.WordUnderCursor) doesnt respect the END_OF_WORD
        for i in range(currentPos, max(-1, currentPos - 128), -1):
            char = text_type(self.document().characterAt(i))
            if char in self.END_OF_WORD:
                startPos = i+1
                break;

        tc.setPosition(startPos, QTextCursor.KeepAnchor)

        text = tc.selectedText()

        return text_type(text)

    def focusInEvent(self, event):
        if self._completer:
            self._completer.setWidget(self);
        QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if not self._completer:
            return QTextEdit.keyPressEvent(self, event)
        if self._completer and self._completer.popup().isVisible():
            if event.key() in (
            Qt.Key_Enter,
            Qt.Key_Return,
            Qt.Key_Escape,
            Qt.Key_Tab,
            Qt.Key_Backtab):
                event.ignore()
                return

        ## has ctrl-E been pressed??
        isShortcut = self._isShortCut(event)
        if (not self._completer or not isShortcut):
            QTextEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (Qt.ControlModifier ,
                Qt.ShiftModifier)
        if ctrlOrShift and event.text().isEmpty():
            # ctrl or shift key on it's own
            return

        hasModifier = ((event.modifiers() != Qt.NoModifier) and
                        not ctrlOrShift)

        completionPrefix = self.textUnderCursor()

        eventText = text_type(event.text())

        if not isShortcut and (hasModifier or not len(eventText) or
        not self._shouldComplete(completionPrefix) or
        eventText[-1] in self.END_OF_WORD):
            self._completer.popup().hide()
            return

        if (completionPrefix != self._completer.completionPrefix()):
            self._completer.setCompletionPrefix(completionPrefix)
            popup = self._completer.popup()
            popup.setCurrentIndex(
                self._completer.completionModel().index(0,0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0)
            + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr) ## popup it up!

    def _shouldComplete(self, completionPrefix):
        if self.completionTrigger and not \
            completionPrefix.startswith(self.completionTrigger):
            return False
        return (len(completionPrefix) >= self.minimalCompletionChars)

    def _isShortCut(self, event):
        return (event.modifiers() == Qt.ControlModifier and
                      event.key() == Qt.Key_Space)

if __name__ == "__main__":
    from PyQt4.QtGui import QApplication, QKeySequence
    app = QApplication([])

    class DictionaryCompleter(QCompleter):
        def __init__(self, parent=None):
            words = []
            try:
                f = open("/usr/share/dict/american","r")
                for word in f:
                    words.append(word.strip())
                f.close()
            except IOError:
                print("dictionary not in anticipated location")
            QCompleter.__init__(self, words, parent)
    completer = DictionaryCompleter()
    te = CompletionTextEdit()
    te.setCompleter(completer)
    
    STARTTEXT = ('This TextEdit provides autocompletions for words that have ' +
'more than 3 characters.\nYou can trigger autocompletion using %s\n\n'''% (
QKeySequence("Ctrl+E").toString(QKeySequence.NativeText)))
    
    te.show()
    app.exec_()
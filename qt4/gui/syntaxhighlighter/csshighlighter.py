from PyQt4.QtGui import QSyntaxHighlighter, QTextCharFormat
from PyQt4.QtCore import Qt
#http://searchcode.com/codesearch/view/33945919
class CssHighlighter(QSyntaxHighlighter):

    Selector = 0
    Property = 1
    Value = 2
    Pseudo = 3
    Pseudo1 = 4
    Pseudo2 = 5
    Quote = 6
    MaybeComment = 7
    Comment = 8
    MaybeCommentEnd = 9

    ALNUM = 0
    LBRACE = 1
    RBRACE = 2
    COLON = 3
    SEMICOLON = 4
    COMMA = 5
    QUOTE = 6
    SLASH = 7
    STAR = 8

    transitions = (
        (Selector, Property, Selector, Pseudo,    Property, Selector, Quote, MaybeComment, Selector), #Selector
        (Property, Property, Selector, Value,     Property, Property, Quote, MaybeComment, Property), #Property
        (Value,    Property, Selector, Value,     Property, Value,    Quote, MaybeComment, Value), #Value
        (Pseudo1, Property, Selector, Pseudo2,    Selector, Selector, Quote, MaybeComment, Pseudo), #Pseudo
        (Pseudo1, Property, Selector, Pseudo,    Selector, Selector, Quote, MaybeComment, Pseudo1), #Pseudo1
        (Pseudo2, Property, Selector, Pseudo,    Selector, Selector, Quote, MaybeComment, Pseudo2), #Pseudo2
        (Quote,    Quote,    Quote,    Quote,     Quote,    Quote,   -1, Quote, Quote), #Quote
        (-1, -1, -1, -1, -1, -1, -1, -1, Comment), #MaybeComment
        (Comment, Comment, Comment, Comment, Comment, Comment, Comment, Comment, MaybeCommentEnd), #Comment
        (Comment, Comment, Comment, Comment, Comment, Comment, Comment, -1, MaybeCommentEnd) #MaybeCommentEnd
    )

    def highlightBlock(self, text):

        lastIndex = 0
        lastWasSlash = False
        state = self.previousBlockState()
        saveState = 0

        if state == -1 or state > 8:
            #As long as the text is empty, leave the state undetermined
            if text.isEmpty():
                self.setCurrentBlockState(-1)
                return
            '''The initial state is based on the precense of a : and the absense of a {.
               This is because Qt style sheets support both a full stylesheet as well as
               an inline form with just properties.'''
            if text.indexOf(':') > -1 and text.indexOf('{') == -1:
                state = saveState = CssHighlighter.Property
            else:
                state = saveState = CssHighlighter.Selector
        else:
            #state = state>>16
            #saveState = state
            #print "before", state

            saveState = state>>16
            #state = 255
            #state = 0x00ff
            #state = saveState + 0
            #print saveState, state

        if state == CssHighlighter.MaybeCommentEnd:
            state = CssHighlighter.Comment
        elif state == CssHighlighter.MaybeComment:
            state = saveState

        for i in range(text.length()):
            token = CssHighlighter.ALNUM
            c = text.at(i)
            a = unicode(c)

            if state == CssHighlighter.Quote:
                if a == '\\':
                    lastWasSlash = True
                else:
                    if a == '"' and not lastWasSlash:
                        token = CssHighlighter.QUOTE
                    lastWasSlash = False
            else:
                if a == '{':
                    token = CssHighlighter.LBRACE
                elif a == '}':
                    token = CssHighlighter.RBRACE
                elif a == ':':
                    token = CssHighlighter.COLON
                elif a == ';':
                    token = CssHighlighter.SEMICOLON
                elif a == ',':
                    token = CssHighlighter.COMMA
                elif a == '"':
                    token = CssHighlighter.QUOTE
                elif a == '/':
                    token = CssHighlighter.SLASH
                elif a == '*':
                    token = CssHighlighter.STAR

            try:
                newState = CssHighlighter.transitions[state][token]
            except IndexError:
                #TODO: Dirty Fix
                #try:
                    #newState = CssHighlighter.transitions[(state>>16)][token]
                #except IndexError:
                    #print "newState is", state, token, (state>>16)
                    #newState = -1
                newState = -1

            if newState != state:
                if newState == CssHighlighter.MaybeCommentEnd \
                    or (state == CssHighlighter.MaybeCommentEnd and newState != CssHighlighter.Comment) \
                    or state == CssHighlighter.Quote:
                    includeToken = 1
                else:
                    includeToken = 0

                self.highlight(text, lastIndex, i-lastIndex+includeToken, state)

                if newState == CssHighlighter.Comment:
                    lastIndex = i-1 #include the slash and star
                else:
                    if token == CssHighlighter.ALNUM or newState == CssHighlighter.Quote:
                        lastIndex = i
                    else:
                        lastIndex = i + 1

            if newState == -1:
                state = saveState
            elif state <= CssHighlighter.Pseudo2:
                saveState = state
                state = newState
            else:
                state = newState

        self.highlight(text, lastIndex, text.length() - lastIndex, state)
        nextState = state + (saveState<<16)
        #try:
            #print "nextState", nextState, state, CssHighlighter.translateState(state)
        #except IndexError:
            #print "no state found for state", state
        self.setCurrentBlockState(nextState)

    def highlight(self, text, start, length, state):
        if start >= text.length() or length <= 0:
            return

        format = QTextCharFormat()

        if state == CssHighlighter.Selector:
            self.setFormat(start, length, Qt.darkRed)
        elif state == CssHighlighter.Property:
            self.setFormat(start, length, Qt.blue)
        elif state == CssHighlighter.Value:
            self.setFormat(start, length, Qt.black)
        elif state == CssHighlighter.Pseudo1:
            self.setFormat(start, length, Qt.darkRed)
        elif state == CssHighlighter.Pseudo2:
            self.setFormat(start, length, Qt.darkRed)
        elif state == CssHighlighter.Quote:
            self.setFormat(start, length, Qt.darkMagenta)
        elif state in (CssHighlighter.Comment, CssHighlighter.MaybeCommentEnd):
            format.setForeground(Qt.darkGreen)
            self.setFormat(start, length, format)
    
    @staticmethod
    def translateState(state):
        states = (
        'Selector',
        'Property',
        'Value',
        'Pseudo',
        'Pseudo1',
        'Pseudo2',
        'Quote',
        'MaybeComment',
        'Comment',
        'MaybeCommentEnd'
        )
        return states[state]
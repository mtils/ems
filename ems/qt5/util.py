
import os.path

def qmlImportPath(compiled=False):
    if not compiled:
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),'..','qt5','assets','qml'
            )
        )
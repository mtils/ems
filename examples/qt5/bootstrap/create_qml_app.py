
import os.path

#from ems.qt4.application import MainApplication
from ems.qt5.qmlwidget_app import App
from ems.support.bootstrappers.validation import ValidationBootstrapper
from ems.support.bootstrappers.qml_application import QmlApplicationBootstrapper

#from examples.qt4.bootstrap.scaffolding import ScafffoldingBootstrapper

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))

def create_app(argv, appPath, env=None):

    env = 'production' if env is None else env

    app = App(argv, appPath)
    app.setQuitOnLastWindowClosed(True)

    app.addBootstrapper(ValidationBootstrapper())
    app.addBootstrapper(QmlApplicationBootstrapper())

    return app
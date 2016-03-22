
import os.path

from ems.app import App
from ems.support.bootstrappers.validation import ValidationBootstrapper

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))

def create_app(argv, appPath, env=None):

    env = 'production' if env is None else env

    app = App(argv, appPath)

    app.addBootstrapper(ValidationBootstrapper())

    return app
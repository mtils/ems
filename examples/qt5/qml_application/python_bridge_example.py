
import os.path

from PyQt5.QtCore import QUrl

from ems.app import app, app_path

from examples.bootstrap.seeding.orm import Contact, Base, ContactNote

class Person:
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

class FloatGenerator:

    def multiply(self, a, b):
        return a * b

class IntGenerator:

    def add(self, a, b):
        return a + b

class StringGenerator:

    def hello(self, a=''):
        return "Hello {}".format(a)

class BoolGenerator:

    def opposite(self, a):
        return not a

class DictGenerator:

    def sample(self):
        return {
            "this": "is",
            "a":"dict",
            "yes":True,
            "count":4
        }

class ListGenerator:

    def sample(self):
        return [
            {
                "this": "is",
                "a":"dict",
                "yes":True,
                "count":4
            },
            {
                "this": "is",
                "a":"second dict",
                "yes":False,
                "count":5,
                "foo": 4.5
            }
        ]

class ObjectGenerator:
    def samples(self):
        return [
            Person(name='Gelb',firstname='Olaf'),
            Person(name='Orange',firstname='Gandalf')
        ]

app().bind('floats', FloatGenerator)
app().bind('ints', IntGenerator)
app().bind('strings', StringGenerator)
app().bind('bools', BoolGenerator)
app().bind('dicts', DictGenerator)
app().bind('lists', ListGenerator)
app().bind('objects', ObjectGenerator)

def changeFloatArguments(args):
    print("calling FloatGenerator.multiply({0}, {1})".format(*args))
    args[0] = 7.0
    print("Changing to ({0}, {1})...".format(*args))

app("events").fire("auth.loggedIn")
app("events").listen("qml-factory.calling:floats.multiply", changeFloatArguments)

qmlFile = os.path.join(app_path(), "examples", "qt5", "qml", "Views", "PythonBridgeExample.qml")

app("events").fire("qml.apply-url", QUrl.fromLocalFile(qmlFile))


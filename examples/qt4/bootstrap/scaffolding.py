
from PyQt4.QtCore import QString
from PyQt4.QtGui import QPixmap

from ems.app import Bootstrapper

from ems.qt4.gui.mapper.base import MapperDefaults
from ems.qt4.gui.mapper.strategies.string_strategy import StringStrategy
from ems.qt4.gui.mapper.strategies.bool_strategy import BoolStrategy
from ems.qt4.gui.mapper.strategies.number_strategy import NumberStrategy
from ems.qt4.gui.mapper.strategies.date_strategy import DateStrategy
from ems.qt4.gui.mapper.strategies.listofdicts_strategy import ListOfDictsStrategy
from ems.qt4.gui.mapper.strategies.oneofalist_strategy import OneOfAListStrategy
from ems.qt4.gui.mapper.strategies.objectinstance_strategy import ObjectInstanceStrategy
from ems.qt4.gui.mapper.strategies.dict_strategy import DictStrategy
from ems.qt4.gui.mapper.strategies.filesystem_strategy import FileSystemStrategy

class ScafffoldingBootstrapper(Bootstrapper):

    def bootstrap(self, app):

        mapperDefaults = MapperDefaults.getInstance()
        mapperDefaults.addStrategy(StringStrategy())
        boolStrategy = BoolStrategy()
        boolStrategy.valueNames = {
            True: QString.fromUtf8('Wahr'),
            False: QString.fromUtf8('Falsch'),
            None: QString.fromUtf8('Keine Angabe')
        }
        mapperDefaults.addStrategy(boolStrategy)
        mapperDefaults.addStrategy(NumberStrategy())
        mapperDefaults.addStrategy(DateStrategy())
        listOfDictStrategy = ListOfDictsStrategy()
        listOfDictStrategy.addPixmap = QPixmap(':/edit/core-icons/22x22/edit_add.png')
        listOfDictStrategy.removePixmap = QPixmap(':/edit/core-icons/22x22/edit_remove.png')
        mapperDefaults.addStrategy(listOfDictStrategy)
        mapperDefaults.addStrategy(OneOfAListStrategy())
        mapperDefaults.addStrategy(ObjectInstanceStrategy())
        mapperDefaults.addStrategy(DictStrategy())
        mapperDefaults.addStrategy(FileSystemStrategy())
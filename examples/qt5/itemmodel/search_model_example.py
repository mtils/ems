
from PyQt5.QtWidgets import QMainWindow, QTableView, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy

from examples.bootstrap.seeding.orm import Contact, Base
from examples.bootstrap.seeding.seeds import seed_contacts

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository

from ems.qt5.itemmodel.search_model import SearchModel


def createMainWindow():
    win = QMainWindow()
    win.setCentralWidget(QWidget())
    win.centralWidget().setLayout(QHBoxLayout())

    win.view = QTableView(win.centralWidget())
    win.view.setSelectionMode(win.view.ContiguousSelection)
    win.centralWidget().layout().addWidget(win.view)
    win.buttonContainer = QWidget(win.centralWidget())
    win.centralWidget().layout().addWidget(win.buttonContainer)

    win.buttonContainer.setLayout(QVBoxLayout())
    win.saveButton = QPushButton('&Save')
    win.buttonContainer.layout().addWidget(win.saveButton)

    win.cancelButton = QPushButton('&Cancel')
    win.buttonContainer.layout().addWidget(win.cancelButton)

    win.addButton = QPushButton('&Add')
    win.buttonContainer.layout().addWidget(win.addButton)

    win.removeButton = QPushButton('&Remove')
    win.buttonContainer.layout().addWidget(win.removeButton)

    win.buttonContainer.layout().addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    return win

class AddRemoveHandler:

    def __init__(self, view):
        self.view = view
        self.model = view.model()
        self.model.error.connect(self.printError)

    def addAfterLastSelected(self):

        selectionModel = self.view.selectionModel()

        if not selectionModel.hasSelection():
            self.model.appendNew()
            return
        rows = self.collectSelectedRows()
        self.model.insertRows(max(rows)+1, len(rows))


    def removeSelected(self):

        selectionModel = self.view.selectionModel()

        if not selectionModel.hasSelection():
            return

        rows = self.collectSelectedRows()

        self.model.removeRows(min(rows), len(rows))

    def collectSelectedRows(self):
        selectionModel = self.view.selectionModel()
        rows = []
        for index in selectionModel.selectedIndexes():
            rows.append(index.row())
        return rows

    def printError(self, exception):
        print(exception)

engine = create_engine('sqlite:///:memory:', echo=True)

Base.metadata.create_all(engine)

sessionMaker = sessionmaker(expire_on_commit=False)
sessionMaker.configure(bind=engine)
session = sessionMaker()

seed_contacts(session)

search = OrmSearch(session, Contact)
columns = [str(c).split('.')[1] for c in Contact.__table__.columns]
search.withKey(*columns)

repository = OrmRepository(Contact, session)
#search.withKey('id', 'contact_type', 'forename', 'surname', 'company', 'phone')

model = SearchModel(search, repository)

win = createMainWindow()
win.view.setModel(model)

win.saveButton.clicked.connect(model.submit)
win.cancelButton.clicked.connect(model.revert)

win.saveButton.setEnabled(model.isDirty())
win.cancelButton.setEnabled(model.isDirty())

model.dirtyStateChanged.connect(win.saveButton.setEnabled)
model.dirtyStateChanged.connect(win.cancelButton.setEnabled)

win.handler = AddRemoveHandler(win.view)

win.addButton.clicked.connect(win.handler.addAfterLastSelected)
win.removeButton.clicked.connect(win.handler.removeSelected)
win.show()

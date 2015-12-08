
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QSpinBox

from examples.bootstrap.seeding.orm import Contact, Base, ContactNote
from examples.qt5.helpers.table_manager import TableManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from examples.bootstrap.seeding.seeds import seed_contacts, seed_contact_notes

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository
from ems.resource.sqlalchemy.helpers import ToManySynchronizer

from ems.qt5.itemmodel.search_model import SearchModel
#from ems.qt5.itemmodel.sequencecolumn_model import SequenceColumnModel
from ems.qt5.itemmodel.current_row_proxymodel import CurrentRowProxyModel

engine = create_engine('sqlite:///:memory:', echo=True)

Base.metadata.create_all(engine)

sessionMaker = sessionmaker(expire_on_commit=False)
sessionMaker.configure(bind=engine)
session = sessionMaker()

seed_contacts(session)
seed_contact_notes(session)

search = OrmSearch(session, Contact)
columns = [str(c).split('.')[1] for c in Contact.__table__.columns]

search.withKey('id', 'contact_type', 'forename', 'surname', 'company')

class ContactRepository(OrmRepository):

    def store(self, attributes, obj=None):

        instance = super().store(self._withoutRelations(attributes), obj)

        if 'notes' in attributes:
            sync = ToManySynchronizer(Contact.notes)
            sync.syncRelation(instance, attributes['notes'])
            session = self._modelSession(instance)
            session.add(instance)
            session.commit()

        return instance

    def update(self, model, changedAttributes):

        if 'notes' in changedAttributes:
            sync = ToManySynchronizer(Contact.notes)
            sync.syncRelation(model, changedAttributes['notes'])

        return super().update(model, self._withoutRelations(changedAttributes))

    def _withoutRelations(self, data):
        cleanedAttributes = {}

        for key, value in data.items():
            if key == 'notes':
                continue
            cleanedAttributes[key] = value

        return cleanedAttributes

repository = ContactRepository(Contact, session)

model = SearchModel(search, repository)

win = QWidget()
win.setWindowFlags(Qt.Dialog)
win.setLayout(QVBoxLayout())
win.setMinimumWidth(800)
win.setMinimumHeight(800)

modelManager = TableManager()
modelManager.setModel(model)

win.layout().addWidget(modelManager)

win.detailWin = QTableView(win)

#noteRepository = OrmRepository(ContactNote, session)

detailModel = CurrentRowProxyModel()
detailModel.setSourceModel(model)
#detailModel.search.withKey('id', 'contact_id', 'memo')
#detailModel.sourceColumn = search.keys.index('notes')
#detailModel.setParentModel(model)

modelManager.selectedRowChanged.connect(detailModel.setCurrentRow)
win.detailWin.setModel(detailModel)

win.layout().addWidget(win.detailWin)

buttonContainer = QWidget(win)
buttonContainer.setLayout(QHBoxLayout())

prevButton = QPushButton("<", buttonContainer)
buttonContainer.layout().addWidget(prevButton)

prevButton.setEnabled(detailModel.hasPrevious)
detailModel.hasPreviousChanged.connect(prevButton.setEnabled)
prevButton.clicked.connect(detailModel.previous)

currentIndexInput = QSpinBox(buttonContainer)
currentIndexInput.setMaximumWidth(100)
currentIndexInput.setReadOnly(True)
currentIndexInput.setMinimum(-1)
currentIndexInput.setMaximum(1000)

detailModel.currentRowChanged.connect(currentIndexInput.setValue)
buttonContainer.layout().addWidget(currentIndexInput)

nextButton = QPushButton(">", buttonContainer)
buttonContainer.layout().addWidget(nextButton)
nextButton.setEnabled(detailModel.hasNext)
nextButton.clicked.connect(detailModel.next)
print("setted button to", detailModel.hasNext)
detailModel.hasNextChanged.connect(nextButton.setEnabled)
print("connected")

win.layout().addWidget(buttonContainer)
buttonContainer.setEnabled(detailModel.isValid)
detailModel.isValidChanged.connect(buttonContainer.setEnabled)

detailModel.currentRowChanged.connect(modelManager.selectRow)

win.show()



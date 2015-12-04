
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from examples.bootstrap.seeding.orm import Contact, Base, ContactNote
from examples.qt5.helpers.table_manager import TableManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from examples.bootstrap.seeding.seeds import seed_contacts, seed_contact_notes

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository
from ems.resource.sqlalchemy.helpers import ToManySynchronizer

from ems.qt5.itemmodel.search_model import SearchModel
from ems.qt5.itemmodel.sequencecolumn_model import SequenceColumnModel

engine = create_engine('sqlite:///:memory:', echo=True)

Base.metadata.create_all(engine)

sessionMaker = sessionmaker(expire_on_commit=False)
sessionMaker.configure(bind=engine)
session = sessionMaker()

seed_contacts(session)
seed_contact_notes(session)

search = OrmSearch(session, Contact)
columns = [str(c).split('.')[1] for c in Contact.__table__.columns]
#search.withKey(*columns)
search.withKey('id', 'contact_type', 'forename', 'surname', 'company', 'notes')

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

modelManager = TableManager()
modelManager.setModel(model)

win.layout().addWidget(modelManager)

win.detailWin = TableManager(win)

#noteRepository = OrmRepository(ContactNote, session)

detailModel = SequenceColumnModel()
detailModel.search.withKey('id', 'contact_id', 'memo')
detailModel.sourceColumn = search.keys.index('notes')
detailModel.setParentModel(model)

modelManager.selectedRowChanged.connect(detailModel.setCurrentRow)
win.detailWin.setModel(detailModel)

win.layout().addWidget(win.detailWin)

win.show()



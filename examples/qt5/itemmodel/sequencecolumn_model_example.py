
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from examples.bootstrap.seeding.orm import Contact, Base, ContactNote
from examples.qt5.helpers.table_manager import TableManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from examples.bootstrap.seeding.seeds import seed_contacts, seed_contact_notes

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository

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

    def update(self, model, changedAttributes):

        cleanedAttributes = {}

        for key, value in changedAttributes.items():
            if key == 'notes':
                self._syncNotes(model, value)
                continue
            cleanedAttributes[key] = value

        return super().update(model, cleanedAttributes)

    def _syncNotes(self, model, notesDict):

        dictIds = self._collectDictNoteIds(notesDict)
        notes = model.notes
        self._deleteMissingNotes(notes, dictIds)
        self._updateExistingNotes(notes, notesDict)
        self._createNewNotes(notes, notesDict)

    def _deleteMissingNotes(self, notes, dictIds):

        deletes = []
        for note in notes:
            if note.id not in dictIds:
                deletes.append(note)

        for note in deletes:
            notes.remove(note)

    def _createNewNotes(self, notes, notesDict):

        for noteDict in notesDict:
            if 'id' in noteDict and noteDict['id'] is not None:
                continue
            notes.append(ContactNote(**noteDict))

    def _updateExistingNotes(self, notes, notesDict):

        notesById = self._notesById(notes)

        for noteDict in notesDict:

            if 'id' not in noteDict or noteDict['id'] is None:
                continue

            if not noteDict['id'] in notesById:
                continue

            note = notesById[noteDict['id']]

            for key, value in noteDict.items():
                if value != getattr(note, key):
                    setattr(note, key, value)

    def _collectDictNoteIds(self, notes):
        return [note['id'] for note in notes if 'id' in note and note['id'] is not None]

    def _notesById(self, notes):
        byId = {}
        for note in notes:
            byId[note.id] = note
        return byId

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

noteRepository = OrmRepository(ContactNote, session)

detailModel = SequenceColumnModel(noteRepository, model)
detailModel.search.withKey('id', 'contact_id', 'memo')
detailModel.sourceColumn = search.keys.index('notes')

modelManager.selectedRowChanged.connect(detailModel.setCurrentRow)
win.detailWin.setModel(detailModel)

win.layout().addWidget(win.detailWin)

win.show()



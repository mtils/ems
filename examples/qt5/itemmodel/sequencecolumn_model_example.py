
from PyQt5.QtCore import Qt

from examples.bootstrap.seeding.orm import Contact, Base, ContactNote
from examples.qt5.helpers.table_manager import TableManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from examples.bootstrap.seeding.seeds import seed_contacts, seed_contact_notes

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository

from ems.qt5.itemmodel.search_model import SearchModel
from ems.qt5.itemmodel.sequencecolumn_model import SequenceColumnModel

engine = create_engine('sqlite:///:memory:', echo=False)

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

repository = OrmRepository(Contact, session)


model = SearchModel(search, repository)

win = TableManager()
win.setModel(model)

win.detailWin = TableManager(win)
win.detailWin.setWindowFlags(Qt.Dialog)

noteRepository = OrmRepository(ContactNote, session)

detailModel = SequenceColumnModel(noteRepository, model)
detailModel.search.withKey('id', 'contact_id', 'memo')
detailModel.sourceColumn = search.keys.index('notes')

win.selectedRowChanged.connect(detailModel.setCurrentRow)

win.show()
win.detailWin.setModel(detailModel)
win.detailWin.show()

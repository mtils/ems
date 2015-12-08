
import os.path

from PyQt5.QtCore import QUrl

from ems.app import app, app_path

from examples.bootstrap.seeding.orm import Contact, Base, ContactNote

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from examples.bootstrap.seeding.seeds import seed_contacts, seed_contact_notes

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository
from ems.qt5.itemmodel.search_model import SearchModel

engine = create_engine('sqlite:///:memory:', echo=False)

Base.metadata.create_all(engine)

sessionMaker = sessionmaker(expire_on_commit=False)
sessionMaker.configure(bind=engine)
session = sessionMaker()

seed_contacts(session)
seed_contact_notes(session)

search = OrmSearch(session, Contact)
columns = [str(c).split('.')[1] for c in Contact.__table__.columns]
search.withKey('id', 'contact_type', 'forename', 'surname', 'company', 'phone', 'fax', 'memo')

repository = OrmRepository(Contact, session)

model = SearchModel(search, repository)

app().shareInstance('contacts.model', model)


app("events").fire("auth.loggedIn")

qmlFile = os.path.join(app_path(), "examples", "qt5", "qml", "Views", "IndexTableEditorExample.qml")

app("events").fire("qml.apply-url", QUrl.fromLocalFile(qmlFile))


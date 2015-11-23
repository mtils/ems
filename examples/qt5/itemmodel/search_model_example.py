
from examples.bootstrap.seeding.orm import Contact, Base
from examples.bootstrap.seeding.seeds import seed_contacts
from examples.qt5.helpers.table_manager import TableManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ems.search.sqlalchemy.orm_search import OrmSearch
from ems.resource.sqlalchemy.repository import OrmRepository

from ems.qt5.itemmodel.search_model import SearchModel

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

win = TableManager()
win.setModel(model)

win.show()

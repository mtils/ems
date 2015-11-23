

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy import UniqueConstraint, Boolean, Float, Text, SmallInteger
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_type = Column(Enum('PERSON','ORGANISATION'), nullable=False)
    forename = Column(String(64), nullable=True)
    surname = Column(String(64), nullable=True)
    company = Column(String(64), nullable=True)
    phone = Column(String(64))
    fax = Column(String(64))
    email = Column(String(255), nullable=True)
    email2 = Column(String(255), nullable=True)
    street = Column(String(255), nullable=True)
    postcode = Column(String(5), nullable=True)
    location = Column(String(16), nullable=True)
    address_addition = Column(String(255), nullable=True)
    memo = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)

class ContactNote(Base):
    __tablename__ = 'contact_notes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id = Column(ForeignKey('contacts.id'))
    memo = Column(Text, nullable=False)
    contact = relationship("Contact", backref=backref('notes', order_by=id))
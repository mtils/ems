
from examples.bootstrap.seeding.orm import Contact, ContactNote

def seed_contacts(session):

    contactData = [
        {
            'contact_type': 'PERSON',
            'forename': 'John',
            'surname': 'Doe',
            'company': 'Century Fox',
            'phone': '0030 6642 45448',
            'fax'  : '0030 6642 45449',
            'email': 'john@doe.com',
            'email2': 'john2@doe.com',
            'street': 'Hollywood Blvd',
            'postcode': '8558-455',
            'location': 'Los Angeles',
            'address_addition': 'Ask Peter',
            'memo': 'Average dude',
            'image': 'http://avatar.com/sdhu98zhu',
        },
        {
            'contact_type': 'PERSON',
            'forename': 'Bettina',
            'surname': 'Doe',
            'company': 'AT & T',
            'phone': '0030 6642 45446',
            'fax'  : '0030 6642 45445',
            'email': 'bettina@doe.com',
            'email2': 'bettina@gmail.com',
            'street': 'Westminster Street',
            'postcode': '8558-457',
            'location': 'London',
            'address_addition': '',
            'memo': 'Moved from Los Angeles to London',
            'image': 'http://avatar.com/sdhu98zh7',
        },
        {
            'contact_type': 'ORGANISATION',
            'forename': 'Michael',
            'surname': 'Tils',
            'company': 'web-utils.de',
            'phone': '0049 721 12345678',
            'fax'  : '0049 721 12345679',
            'email': 'mtils@web-utils.de',
            'email2': 'mtils@web-utils.de',
            'street': 'Strasse 10',
            'postcode': '76000',
            'location': 'Karlsruhe',
            'address_addition': '',
            'memo': 'The guy who created this seeder',
            'image': 'http://avatar.com/sdhu98zh19',
        }
    ]

    for data in contactData:
        contact = Contact(**data)
        session.add(contact)

    session.commit()

def seed_contact_notes(session):

    notes = [
        {
            'memo': 'Has pets'
        },
        {
            'memo': 'Loves Music'
        },
        {
            'memo': 'Has a loud voice'
        }
    ]

    contact = session.query(Contact).first()

    for data in notes:
        note = ContactNote(**data)
        note.contact_id = contact.id
        session.add(note)

    session.commit()
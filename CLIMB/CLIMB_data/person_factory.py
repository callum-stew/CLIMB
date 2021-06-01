from CLIMB import db
from .person import Staff, Member, Admin


def create_person(account_user_type, person_id=None):
    if account_user_type == 'STAFF':
        return Staff(person_id)
    elif account_user_type == 'ADMIN':
        return Admin(person_id)
    elif account_user_type == 'MEMBER':
        return Member(person_id)


def person_from_id(person_id):
    cur = db.connection.cursor()
    cur.execute('SELECT user_type FROM person WHERE person_id=? AND deleted=0', (person_id,))
    data = cur.fetchone()
    if data:
        return create_person(data['user_type'], person_id)
    else:
        raise KeyError("person id not in database")


def person_from_email(email):
    cur = db.connection.cursor()
    cur.execute('SELECT user_type, person_id FROM person WHERE email=? AND deleted=0', (email,))
    data = cur.fetchone()
    if data:
        return create_person(data['user_type'], data['person_id'])
    else:
        raise KeyError("email not in database")

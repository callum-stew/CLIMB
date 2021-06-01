from datetime import date

from CLIMB import db
from .data import PersonData, LoginData, PersonHasPermissionData

PERMISSIONS = ['STORE_CONFIG',
               'SETTINGS',
               'BOOKINGS',
               'TRANSACTIONS',
               'FORMS',
               'MAKE_TRANSACTIONS',
               'VIEW_TRANSACTIONS',
               'MEMBER_DATA',
               'STAFF_DATA']


def permission_id_from_name(permission_name):
    cur = db.connection.cursor()
    cur.execute('SELECT permission_id FROM permission WHERE name = ?', (permission_name,))
    data = cur.fetchone()
    return data['permission_id']


class Person:
    """Base class for interactions with person"""

    _user_type = None
    _permissions = []

    def __init__(self, person_id):
        self._person_data = PersonData(person_id)
        self._person_id = self._person_data['person_id']
        self._login_data = LoginData(self._person_id)
        self._permission_data = PersonHasPermissionData()
        self._permissions = []

        if self._person_data.created:
            for permission in self._permission_data.get_items(person_id=self.person_id):
                self._permissions.append(permission[1]['name'])

    def create(self):
        if self._person_data.created:
            return False

        self._person_data['registration_date'] = date.today()

        valid, issue = self._person_data.data_valid()
        if not valid and issue != ['person_id']:
            raise ValueError(issue)

        self._person_data.create()
        self._person_id = self._person_data['person_id']

        if self._login_data['password_hash']:
            self._login_data['person_id'] = self._person_id
            self._login_data.create()

        for permission_name in self.permissions:
            self._permission_data.add_item(self.person_id, permission_id_from_name(permission_name), {})

    def delete(self, safe=True):
        if self._login_data.created:
            self._login_data.delete()

        if not safe:
            if self._person_data.created:
                self._person_data.delete()
        else:
            self._person_data['deleted'] = 1
            self.first_name = None
            self.middle_name = None
            self.last_name = None
            self.address_line_1 = None
            self.address_line_2 = None
            self.email = None
            self.mobile_phone = None
            self.home_phone = None
            self.date_of_birth = None
            self.emergency_name = None
            self.emergency_phone = None

    @property
    def person_id(self):
        return self._person_id

    @property
    def deleted(self):
        return self._person_data['deleted']

    @property
    def user_type(self):
        return self._user_type

    @property
    def first_name(self):
        return self._person_data['first_name']

    @first_name.setter
    def first_name(self, value):
        self._person_data['first_name'] = value

    @property
    def middle_name(self):
        return self._person_data['middle_name']

    @middle_name.setter
    def middle_name(self, value):
        self._person_data['middle_name'] = value

    @property
    def last_name(self):
        return self._person_data['last_name']

    @last_name.setter
    def last_name(self, value):
        self._person_data['last_name'] = value

    @property
    def address_line_1(self):
        return self._person_data['address_line_1']

    @address_line_1.setter
    def address_line_1(self, value):
        self._person_data['address_line_1'] = value

    @property
    def address_line_2(self):
        return self._person_data['address_line_2']

    @address_line_2.setter
    def address_line_2(self, value):
        self._person_data['address_line_2'] = value

    @property
    def address_line_3(self):
        return self._person_data['address_line_3']

    @address_line_3.setter
    def address_line_3(self, value):
        self._person_data['address_line_3'] = value

    @property
    def county(self):
        return self._person_data['county']

    @county.setter
    def county(self, value):
        self._person_data['county'] = value

    @property
    def country(self):
        return self._person_data['country']

    @country.setter
    def country(self, value):
        self._person_data['country'] = value

    @property
    def postcode(self):
        return self._person_data['postcode']

    @postcode.setter
    def postcode(self, value):
        self._person_data['postcode'] = value

    @property
    def email(self):
        return self._person_data['email']

    @email.setter
    def email(self, value):
        self._person_data['email'] = value

    @property
    def home_phone(self):
        return self._person_data['home_phone']

    @home_phone.setter
    def home_phone(self, value):
        self._person_data['home_phone'] = value

    @property
    def mobile_phone(self):
        return self._person_data['mobile_phone']

    @mobile_phone.setter
    def mobile_phone(self, value):
        self._person_data['mobile_phone'] = value

    @property
    def date_of_birth(self):
        return self._person_data['date_of_birth']

    @date_of_birth.setter
    def date_of_birth(self, value):
        self._person_data['date_of_birth'] = value

    @property
    def emergency_name(self):
        return self._person_data['emergency_name']

    @emergency_name.setter
    def emergency_name(self, value):
        self._person_data['emergency_name'] = value

    @property
    def emergency_phone(self):
        return self._person_data['emergency_phone']

    @emergency_phone.setter
    def emergency_phone(self, value):
        self._person_data['emergency_phone'] = value

    @property
    def password_hash(self):
        return self._login_data['password_hash']

    @password_hash.setter
    def password_hash(self, value):
        self._login_data['password_hash'] = value

    @property
    def temp_password(self):
        return self._login_data['temp']

    @temp_password.setter
    def temp_password(self, value):
        self._login_data['temp'] = value

    @property
    def registration_date(self):
        return self._person_data['registration_date']

    @property
    def permissions(self):
        return self._permissions

    def has_permission(self, name):
        if name in self._permissions:
            return True
        else:
            return False

    def add_permission(self, permission_name):
        if permission_name in PERMISSIONS and permission_name not in self.permissions:
            if self._person_data.created:
                self._permission_data.add_item(self.person_id, permission_id_from_name(permission_name), {})
            self.permissions.append(permission_name)

    def remove_permission(self, permission_name):
        if permission_name in PERMISSIONS and permission_name in self.permissions:
            if self._person_data.created:
                self._permission_data.delete_item(self.person_id, permission_id_from_name(permission_name))
            self.permissions.remove(permission_name)


class Staff(Person):
    _user_type = 'STAFF'

    def __init__(self, person_id):
        super().__init__(person_id)

    def create(self):
        self._person_data['user_type'] = 'STAFF'
        super().create()


class Admin(Person):
    _user_type = 'ADMIN'

    def __init__(self, person_id):
        super().__init__(person_id)

    def create(self):
        self._person_data['user_type'] = 'ADMIN'
        super().create()


class Member(Person):
    _user_type = 'MEMBER'

    def __init__(self, person_id):
        super().__init__(person_id)

    def create(self):
        self._person_data['user_type'] = 'MEMBER'
        super().create()

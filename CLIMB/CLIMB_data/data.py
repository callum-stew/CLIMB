from sqlite3 import IntegrityError

from CLIMB import db


class Row:
    """Represents a row in the database.
    Allows data retrieval or setting through class['key'] = value format."""

    _primary_keys = None
    _attributes = None
    _null_attributes = []
    _unique_attributes = []
    _auto_incrementing_attributes = []
    _defaults = {}
    _table = None
    _created = False

    def __init__(self, identifier=None):
        # dict with all fields from table
        self._fields_dict = dict.fromkeys({**self._attributes, **self._primary_keys}.keys(), None)

        if identifier:
            # set class primary key fields using primary keys in identifier and check entry exists in database
            if set(self._primary_keys.keys()) == set(identifier.keys()):
                for field in identifier.keys():
                    self[field] = identifier[field]

                cur = db.connection.cursor()

                query = 'SELECT * FROM '+self._table+' WHERE '
                query, query_parameters = self._query_where_primary_key(query)

                cur.execute(query, tuple(query_parameters))
                data = cur.fetchone()
                if not data:
                    raise KeyError("Primary keys don't exist in database")

            # get database primary keys using unique attribute and check entry exists
            elif len(identifier.keys()) == 1 and identifier.keys()[0] in self._unique_attributes:
                field = identifier.keys()[0]

                cur = db.connection.cursor()

                query = 'SELECT '
                for pk in self._primary_keys.keys():
                    query += (pk + ', ')
                query = query[:-2] + ' FROM ' + self._table + ' WHERE ' + field + ' = ?'

                cur.execute(query, (identifier[field],))
                data = cur.fetchone()
                if not data:
                    raise KeyError("Primary keys don't exist in database")

                for pk in self._primary_keys.keys():
                    self[pk] = data[pk]

            self._created = True

    def __getitem__(self, field):
        """ get value of field in database entry """

        # return from class dict
        if not self._created:
            return self._fields_dict[field]

        # return from database
        cur = db.connection.cursor()

        query = 'SELECT '+field+' FROM '+self._table+' WHERE '
        query, query_parameters = self._query_where_primary_key(query)

        cur.execute(query, tuple(query_parameters))
        data = cur.fetchone()

        return data[field]

    def __setitem__(self, field, value):
        """ Set value of field in database entry """

        # Check value is of correct data type else raise ValueError
        {**self._primary_keys, **self._attributes}[field](value)

        if self._created:
            # if created save to database
            cur = db.connection.cursor()

            query = 'UPDATE '+self._table+' SET '+field+'=? WHERE '
            query_parameters = [value]
            query, query_parameters = self._query_where_primary_key(query, query_parameters)

            # catch errors due to unique and raise key error for that field
            try:
                cur.execute(query, tuple(query_parameters))
            except IntegrityError as e:
                if 'UNIQUE' in str(e):
                    field = str(e).split('.')[1]
                    raise KeyError('field:'+field)
                else:
                    raise IntegrityError(str(e))
            db.connection.commit()

        else:
            # store in class dict
            self._fields_dict[field] = value

    def data_valid(self):
        """ check value for field is of correct data type """

        field_errors = []
        for field in self._fields_dict.keys():
            if field not in self._null_attributes and field not in self._defaults.keys() and self._fields_dict[field] is None:
                field_errors.append(field)

        if field_errors:
            return False, field_errors

        return True, None

    def create(self):
        """ create entry in database """

        cur = db.connection.cursor()

        query = 'INSERT INTO '+self._table+' ('
        query_values = 'VALUES ('
        query_parameters = []
        for field in self._fields_dict.keys():
            if field not in self._auto_incrementing_attributes:
                query += (field+', ')
                query_values += '?, '
                if self._fields_dict[field] is None and field in self._defaults:
                    query_parameters.append(self._defaults[field])
                else:
                    query_parameters.append(self._fields_dict[field])
        query = (query[:-2]+') '+query_values[:-2]+')')

        # catch errors due to unique and raise key error for that field
        try:
            cur.execute(query, tuple(query_parameters))
        except IntegrityError as e:
            if 'UNIQUE' in str(e):
                field = str(e).split('.')[1]
                raise KeyError('field:'+field)
            else:
                raise IntegrityError(str(e))

        row_id = cur.lastrowid
        db.connection.commit()

        # get value of auto incrementing fields using ROWID
        if self._auto_incrementing_attributes:
            query = 'SELECT '
            for field in self._auto_incrementing_attributes:
                query += (field+', ')
            query = (query[:-2]+' FROM '+self._table+' WHERE ROWID=?')

            cur.execute(query, (row_id,))
            data = cur.fetchone()
            for field in data.keys():
                self[field] = data[field]

    def _query_where_primary_key(self, query, query_parameters=None):
        """ create query where primary keys """

        if not query_parameters:
            query_parameters = []
        for primary_key in self._primary_keys.keys():
            if not self._fields_dict[primary_key]:
                raise KeyError('Primary keys not set', primary_key)

            query += (primary_key + '=? AND ')
            query_parameters.append(self._fields_dict[primary_key])
        query = query[:-5]
        return query, query_parameters

    def delete(self):
        """ delete entry from database """

        cur = db.connection.cursor()
        query = 'DELETE FROM '+self._table+' WHERE '
        query, query_parameters = self._query_where_primary_key(query)
        cur.execute(query, tuple(query_parameters))
        db.connection.commit()

    @property
    def created(self):
        return self._created


class ManyToMany:
    """ represents a many to many relationship between two tables """

    _table = ''
    _linked_table_1_data = None
    _primary_key_1 = []
    _linked_table_2_data = None
    _primary_key_2 = []
    _attributes = {}

    def add_item(self, primary_key_1, primary_key_2, attributes):
        """ create entry in relationship table """

        cur = db.connection.cursor()

        # check data types
        self._primary_key_1[1](primary_key_1)
        self._primary_key_2[1](primary_key_2)
        for field in attributes.keys():
            self._attributes[field](attributes[field])

        query = 'INSERT INTO ' + self._table + ' (' + self._primary_key_1[0]\
                + ', ' + self._primary_key_2[0] + ', '
        query_values = 'VALUES (?, ?, '
        query_parameters = [primary_key_1, primary_key_2]
        for field in attributes:
            if field not in self._attributes.keys():
                raise KeyError(field + ' not in ' + self._attributes.keys())
            query += (field + ', ')
            query_values += '?, '
            query_parameters.append(attributes[field])
        query = (query[:-2] + ') ' + query_values[:-2] + ')')

        cur.execute(query, tuple(query_parameters))
        db.connection.commit()

    def update_item(self, primary_key_1, primary_key_2, attributes):
        """ update entry in relationship table """

        cur = db.connection.cursor()
        fields = []
        values = []

        for key in attributes.keys():
            if key not in self._attributes.keys():
                raise KeyError
            fields.append(key)
            values.append(attributes(key))

        query = 'UPDATE ' + self._table + ' SET '
        for field in fields:
            query += field + '=?, '
        query = (query[:-2] + ' WHERE ' + self._primary_key_1[0]
                 + '=? AND ' + self._primary_key_2[0] + '=?')
        values.append(primary_key_1)
        values.append(primary_key_2)

        cur.execute(query, tuple(values))
        db.connection.commit()

    def delete_items(self, primary_key_1=None, primary_key_2=None):
        """ delete entry in relationship table """

        cur = db.connection.cursor()

        query = 'DELETE FROM ' + self._table + ' WHERE ' + self._primary_key_1[0]\
                + '=? AND ' + self._primary_key_2[0] + '=?'

        cur.execute(query, (primary_key_1, primary_key_2))
        db.connection.commit()

    def get_items(self, primary_key_1=None, primary_key_2=None):
        """ get entries in relationship table with 0, 1 or 2 primary keys"""

        cur = db.connection.cursor()
        if primary_key_1 and primary_key_2:
            cur.execute('SELECT * FROM ' + self._table + ' WHERE ' + self._primary_key_1[0]
                        + '=? AND ' + self._primary_key_2[0] + '=?', (primary_key_1, primary_key_2))
            data = cur.fetchall()
            if not data:
                return []
            return self._get_objects_from_data(data)

        elif primary_key_1:
            cur.execute('SELECT * FROM ' + self._table + ' WHERE ' + self._primary_key_1[0]
                        + '=?', (primary_key_1,))
            data = cur.fetchall()
            if not data:
                return []
            return self._get_objects_from_data(data)

        elif primary_key_2:
            cur.execute('SELECT * FROM ' + self._table + ' WHERE ' + self._primary_key_2[0] + '=?', (primary_key_2,))
            data = cur.fetchall()
            if not data:
                return []
            return self._get_objects_from_data(data)

        else:
            return []

    def _get_objects_from_data(self, data):
        """ get a row object for the two entries that are in the relationship """

        response = []
        for row in data:
            row_response = [self._linked_table_1_data(row[self._primary_key_1[0]]),
                            self._linked_table_2_data(row[self._primary_key_2[0]])]
            attribute_response = {}
            for field in self._attributes.keys():
                attribute_response[field] = row[field]
            row_response.append(attribute_response)
            response.append(row_response)
        return response


class PersonData(Row):
    _primary_keys = {'person_id': int}
    _attributes = {'user_type': str,
                   'first_name': str,
                   'middle_name': str,
                   'last_name': str,
                   'address_line_1': str,
                   'address_line_2': str,
                   'address_line_3': str,
                   'county': str,
                   'postcode': str,
                   'email': str,
                   'home_phone': str,
                   'mobile_phone': str,
                   'date_of_birth': str,
                   'emergency_name': str,
                   'emergency_phone': str,
                   'deleted': int,
                   'registration_date': str}
    _unique_attributes = ['email']
    _null_attributes = ['first_name',
                        'middle_name',
                        'last_name',
                        'address_line_1',
                        'address_line_2',
                        'address_line_3',
                        'email',
                        'home_phone',
                        'mobile_phone',
                        'date_of_birth',
                        'emergency_name',
                        'emergency_phone',]
    _auto_incrementing_attributes = ['person_id']
    _defaults = {'deleted': 0}
    _table = 'person'

    def __init__(self, person_id):
        if person_id:
            super().__init__({'person_id': person_id})
        else:
            super().__init__()


class LoginData(Row):
    _primary_keys = {'person_id': int}
    _attributes = {'password_hash': str,
                   'temp': bool}
    _null_attributes = ['temp']
    _defaults = {'temp': 0}
    _table = 'login'

    def __init__(self, person_id):
        if person_id:
            try:
                super().__init__({'person_id': person_id})
            except KeyError:
                super().__init__()
        else:
            super().__init__()


class PermissionData(Row):
    _primary_keys = {'permission_id': int}
    _attributes = {'name': str}
    _unique_attributes = ['name']
    _auto_incrementing_attributes = ['permission_id']
    _table = 'permission'

    def __init__(self, permission_id):
        if permission_id:
            super().__init__({'permission_id': permission_id})
        else:
            super().__init__()


class PersonHasPermissionData(ManyToMany):
    _linked_table_1_data = PersonData
    _primary_key_1 = ['person_id', int]
    _linked_table_2_data = PermissionData
    _primary_key_2 = ['permission_id', int]
    _table = 'person_has_permission'

    def add_item(self, person_id, permission_id, attributes):
        return super().add_item(person_id, permission_id, attributes)

    def delete_item(self, person_id=None, permission_id=None):
        return super().delete_items(person_id, permission_id)

    def get_items(self, person_id=None, permission_id=None):
        return super().get_items(person_id, permission_id)


class ProductData(Row):
    _primary_keys = {'product_id': int}
    _attributes = {'name': str,
                   'price': str,
                   'shop_position': int,
                   'deleted': int}
    _null_attributes = ['shop_position']
    _auto_incrementing_attributes = ['product_id']
    _defaults = {'deleted': 0}
    _table = 'product'

    def __init__(self, product_id):
        if product_id:
            super().__init__({'product_id': product_id})
        else:
            super().__init__()


class SaleData(Row):
    _primary_keys = {'sale_id': int}
    _attributes = {'staff_person_id': int,
                   'member_person_id': int,
                   'date': str}
    _auto_incrementing_attributes = ['sale_id']
    _table = 'sale'

    def __init__(self, sale_id):
        if sale_id:
            super().__init__({'sale_id': sale_id})
        else:
            super().__init__()


class SaleHasProductData(ManyToMany):
    _linked_table_1_data = SaleData
    _primary_key_1 = ['sale_id', int]
    _linked_table_2_data = ProductData
    _primary_key_2 = ['product_id', int]
    _attributes = {'number_of_products': int}
    _table = 'sale_has_product'

    def add_item(self, sale_id, product_id, attributes):
        return super().add_item(sale_id, product_id, attributes)

    def delete_items(self, sale_id=None, product_id=None):
        return super().delete_items(sale_id, product_id)

    def get_items(self, sale_id=None, product_id=None):
        return super().get_items(sale_id, product_id)


class SettingData(Row):
    _primary_keys = {'setting_id': int}
    _attributes = {'name': str,
                   'value': str}
    _unique_attributes = ['name']
    _auto_incrementing_attributes = ['setting_id']
    _table = 'setting'

    def __init__(self, setting_id):
        if setting_id:
            super().__init__({'setting_id': setting_id})
        else:
            super().__init__()


class WeekDaySettingsData(Row):
    _primary_keys = {'day_id': int}
    _attributes = {'day': str,
                   'open': int,
                   'opening_time': str,
                   'closing_time': str}
    _unique_attributes = ['day']
    _null_attributes = ['opening_time', 'closing_time']
    _auto_incrementing_attributes = ['day_id']
    _table = 'weekly_opening_days'

    def __init__(self, day_id):
        if day_id:
            super().__init__({'day_id': day_id})
        else:
            super().__init__()


class CustomDaySettingsData(Row):
    _primary_keys = {'date_id': int}
    _attributes = {'date': str,
                   'open': int,
                   'opening_time': str,
                   'closing_time': str}
    _unique_attributes = ['date']
    _null_attributes = ['opening_time', 'closing_time']
    _auto_incrementing_attributes = ['date_id']
    _table = 'custom_opening_days'

    def __init__(self, date_id):
        if date_id:
            super().__init__({'date_id': date_id})
        else:
            super().__init__()


class BookingData(Row):
    _primary_keys = {'booking_id': int}
    _attributes = {'person_id': int,
                   'start_timestamp': int,
                   'end_timestamp': int,
                   'adults': int,
                   'children': int,
                   'completed': int}
    _defaults = {'completed': 0}
    _auto_incrementing_attributes = ['booking_id']
    _table = 'booking'

    def __init__(self, booking_id):
        if booking_id:
            super().__init__({'booking_id': booking_id})
        else:
            super().__init__()

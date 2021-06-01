from datetime import datetime

from CLIMB import db
from .data import BookingData


class Booking:
    def __init__(self, booking_id=None):
        self._booking_data = BookingData(booking_id)
        self._booking_id = self._booking_data['booking_id']

    def create(self):
        if self._booking_data.created:
            return

        valid, issue = self._booking_data.data_valid()
        if not valid and issue != ['booking_id']:
            raise ValueError(issue)
        self._booking_data.create()
        self._booking_id = self._booking_data['booking_id']

    def delete(self):
        self._booking_data.delete()

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def person_id(self):
        return self._booking_data['person_id']

    @person_id.setter
    def person_id(self, value):
        self._booking_data['person_id'] = value

    @property
    def start(self):
        return self._booking_data['start_timestamp']

    @start.setter
    def start(self, value):
        self._booking_data['start_timestamp'] = value

    @property
    def end(self):
        return self._booking_data['end_timestamp']

    @end.setter
    def end(self, value):
        self._booking_data['end_timestamp'] = value

    @property
    def adults(self):
        return self._booking_data['adults']

    @adults.setter
    def adults(self, value):
        self._booking_data['adults'] = value

    @property
    def children(self):
        return self._booking_data['children']

    @children.setter
    def children(self, value):
        self._booking_data['children'] = value

    @property
    def completed(self):
        return self._booking_data['completed']

    @completed.setter
    def completed(self, value):
        self._booking_data['completed'] = value


def get_bookings_from_person(person_id, get_all=False):
    cur = db.connection.cursor()
    cur.execute('SELECT booking_id FROM booking WHERE person_id=?', (person_id,))
    data = cur.fetchall()
    bookings = []
    for row in data:
        booking = Booking(row['booking_id'])
        if (not get_all and datetime.fromtimestamp(booking.end) < datetime.today()) or (not get_all and booking.completed):
            continue
        bookings.append(booking)
    return bookings


def get_bookings_between_timestamp(start, end):
    cur = db.connection.cursor()
    cur.execute('SELECT booking_id FROM booking WHERE (start_timestamp >= ? and start_timestamp <= ?) or (end_timestamp >= ? and end_timestamp <= ?) or (start_timestamp <= ? and end_timestamp >= ?) ORDER BY start_timestamp', (start, end, start, end, start, end))
    data = cur.fetchall()
    bookings = []
    for row in data:
        booking = Booking(row['booking_id'])
        bookings.append(booking)
    return bookings

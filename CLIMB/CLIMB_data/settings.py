from CLIMB import db
from .data import SettingData, WeekDaySettingsData, CustomDaySettingsData


class Settings:
    """ Object to allow creation and retrieval of settings from the database """

    def __init__(self):
        self._settings = {}
        cur = db.connection.cursor()
        cur.execute('SELECT setting_id FROM setting')
        data = cur.fetchall()
        for row in data:
            setting = SettingData(row['setting_id'])
            self._settings[setting['name']] = setting

    def get(self, setting_name):
        """ Get setting value """

        if setting_name in self._settings.keys():
            return self._settings[setting_name]['value']
        return None

    def set(self, setting_name, value):
        """ Change or create setting """
        
        if setting_name in self._settings.keys():
            self._settings[setting_name]['value'] = value
        else:
            setting = SettingData(None)
            setting['name'] = setting_name
            setting['value'] = value
            setting.create()
            self._settings[setting_name] = setting


class WeekDaySettings:
    """ Settings for each day of the week """

    _ATTRIBUTES = ['open',
                   'opening_time',
                   'closing_time']

    def __init__(self):
        self._days = {}
        cur = db.connection.cursor()
        cur.execute('SELECT day_id FROM weekly_opening_days')
        data = cur.fetchall()
        for row in data:
            day = WeekDaySettingsData(row['day_id'])
            self._days[day['day']] = day

    def set(self, day, **kwargs):
        if day in self._days.keys():
            for field in kwargs.keys():
                if field in self._ATTRIBUTES:
                    self._days[day][field] = kwargs[field]

    def get(self, day):
        return {'open': self._days[day]['open'],
                'opening_time': self._days[day]['opening_time'],
                'closing_time': self._days[day]['closing_time']}


class CustomDaySettings:
    """ settings for a custom day that overides weekday settings """

    _ATTRIBUTES = ['open',
                   'opening_time',
                   'closing_time']

    def __init__(self):
        self._dates = {}
        cur = db.connection.cursor()
        cur.execute('SELECT date_id FROM custom_opening_days')
        data = cur.fetchall()
        for row in data:
            date = CustomDaySettingsData(row['date_id'])
            self._dates[date['date']] = date

    def set(self, date, **kwargs):
        if date not in self._dates.keys():
            self._dates[date] = CustomDaySettingsData(None)
            for field in kwargs.keys():
                if field in self._ATTRIBUTES:
                    self._dates[date][field] = kwargs[field]
            self._dates[date]['date'] = date
            self._dates[date].create()
        else:
            for field in kwargs.keys():
                if field in self._ATTRIBUTES:
                    self._dates[date][field] = kwargs[field]

    def get(self, date):
        return {'open': self._dates[date]['open'],
                'opening_time': self._dates[date]['opening_time'],
                'closing_time': self._dates[date]['closing_time']}

    @property
    def dates(self):
        return self._dates.keys()

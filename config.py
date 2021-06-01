# values such as email password and secret key should be stored in environment variables
# using a python package like dotenv which is not installed on school computers.

class Config:
    # Flask settings
    FLASK_APP = 'wsgi.py'
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True

    SECRET_KEY = 'SECRET_KEY'
    SESSION_COOKIE_NAME = 'CLIMB_sess'

    # Database settings
    DATABASE_NAME = 'CLIMB_DATABASE.sqlite3'

    # Email settings
    SENDER_EMAIL = 'dev.callum.d.stew@gmail.com'
    SENDER_EMAIL_PASSWORD = 'DevPass24'

import smtplib
import ssl


class Email:
    """ Allows emails to be sent from account in config """

    port = 465

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """ Gets sender email and password from config """

        self.app = app
        self.sender_email = app.config['SENDER_EMAIL']
        self.sender_email_password = app.config['SENDER_EMAIL_PASSWORD']
        self.context = ssl.create_default_context()

    def send_email(self, receiver_email, content):
        """ Sends email to receiver address with content """

        try:
            receiver_email = 'callum.d.stew@gmail.com' # for testing purposes overwright reciver
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=self.context) as server:
                server.login(self.sender_email, self.sender_email_password)
                server.sendmail(self.sender_email, receiver_email, content)
        except:
            print(content)  # school firewall blocks sending emails so i print it to console

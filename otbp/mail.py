from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    mail.init_app(app)


def send_mail(email, subject, text):
    message = Message(subject,
                      recipients=[email],
                      body=text)
    mail.send(message)

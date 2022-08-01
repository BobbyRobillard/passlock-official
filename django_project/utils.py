from django.shortcuts import render
from django.core.mail import send_mail


def message_owner(subject, message):
    send_mail(
        subject,
        message,
        'internal-mailing@app.passlock.com',
        ['admin@techandmech.com', 'info@thepasslock.com'],
        fail_silently=False,
    )

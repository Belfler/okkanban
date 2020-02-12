from okkanban.celery import celery_app
from django.core.mail import send_mail


@celery_app.task
def send_mail_async(*args, **kwargs):
    """Asynchronous wrapper for django.core.mail.send_mail()"""
    send_mail(*args, **kwargs)

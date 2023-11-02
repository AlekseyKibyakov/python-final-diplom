import json

from django.conf import settings
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created
import os
from .models import ConfirmEmailToken, User
from dotenv import load_dotenv

load_dotenv()
new_user_registered = Signal('user_id')

new_order = Signal('user_id')

from .tasks import send_email

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Celery-задача для асинхронной отправки письма сброса пароля.
    """
    subject = f"Токен сброса пароля для {reset_password_token.user}"
    message = reset_password_token.key
    from_email = settings.EMAIL_HOST_USER
    to_email = reset_password_token.user.email
    send_email.delay(subject, message, from_email, to_email)

@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    Celery-задача для асинхронной отправки письма с подтверждением почты.
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    subject = f"Токен подтверждения Email для {token.user.email}"
    message = token.key
    from_email = settings.EMAIL_HOST_USER
    to_email = token.user.email
    send_email.delay(subject, message, from_email, to_email)

@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    Celery-задача для асинхронной отправки письма об изменении статуса заказа.
    """
    user = User.objects.get(id=user_id)

    subject = "Обновление статуса заказа"
    message = "Заказ сформирован"
    from_email = settings.EMAIL_HOST_USER
    to_email = user.email
    send_email.delay(subject, message, from_email, to_email)

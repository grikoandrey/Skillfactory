from django.contrib.auth.models import User
from django.core.mail import mail_managers, mail_admins, EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver


# Это я пробовал реализовать сигнал для отправки сообщения при регистрации (первом входе) пользователя
# через аккаунт социальной сети. Но пока безуспешно.
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.socialaccount_set.exists() and not instance.welcome_email_sent:
        # Отправляем приветственное письмо
        subject = 'Добро пожаловать на Новостной портал!'
        message = f'{instance.username}, вы успешно зарегистрировались на сайте!'
        html = (f'<b>{instance.username}</b>, вы успешно зарегистрировались на '
                f'<a href="http://127.0.0.1:8000/portal">сайте</a>!')
        msg = EmailMultiAlternatives(subject=subject, body=message, from_email=None, to=[instance.email])
        msg.attach_alternative(html, "text/html")
        msg.send()
        # Устанавливаем флаг welcome_email_sent в True
        instance.welcome_email_sent = True
        instance.save()
        mail_managers(
            subject='Новый пользователь!',
            message=f'Пользователь {instance.username} зарегистрировался на сайте через соц.сеть.')
        mail_admins(
            subject='Новый пользователь!',
            message=f'Пользователь {instance.username} зарегистрировался на сайте через соц.сеть.')

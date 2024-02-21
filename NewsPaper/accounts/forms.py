from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives, mail_managers, mail_admins


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_users = Group.objects.get(name="general group")
        user.groups.add(common_users)
        subject = 'Добро пожаловать на Новостной портал!'
        message = (f'{user.username}, вы подали заявку на регистрацию на сайте!'
                   f'Сейчас Вам на почту придет ссылка для подтверждения почтового адреса. '
                   f'Пожалуйста перейдите по ней, подтвердите адрес и зайдите в систему через форму "входа". '
                   f'Спасибо за проявленный интерес!')
        html = (f'<b>{user.username}</b>, вы подали заявку на регистрацию на '
                f'<a href="http://127.0.0.1:8000/portal">сайте</a>!<br><br>'
                f'Сейчас Вам на почту придет ссылка для подтверждения почтового адреса.<br>'
                f'Пожалуйста перейдите по ней, подтвердите адрес и зайдите в систему через форму "входа".<br>'
                f'Спасибо за проявленный интерес!')
        msg = EmailMultiAlternatives(subject=subject, body=message, from_email=None, to=[user.email])
        msg.attach_alternative(html, "text/html")
        msg.send()
        mail_managers(  # отправка сообщения менеджерам
            subject='Новый пользователь!',
            message=f'Пользователь {user.username} зарегистрировался на сайте.')
        mail_admins(  # отправка сообщения админам
            subject='Новый пользователь!',
            message=f'Пользователь {user.username} зарегистрировался на сайте.')
        return user

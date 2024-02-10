from django.contrib.auth.models import Group  # импортирует модель Group, представляет группу пользователей
from allauth.socialaccount.models import SocialAccount  # Модель связана с социальными аккаунтами пользователей
from allauth.account.signals import user_signed_up  # импортирует сигнал
from django.dispatch import receiver  # импортирует декоратор receiver для регистрации обработчиков сигналов


# Create your models here.
@receiver(user_signed_up)  # декоратор регистрирует функцию
def add_to_author_group(request, user, **kwargs):  # будет вызываться при срабатывании сигнала
    social_account = SocialAccount.objects.filter(user=user).exists()  # получает объект SocialAccount, связанный
    # с новым пользователем, если регистрация была совершена через социальную сеть
    if social_account:  # проверяет, была ли регистрация пользователя через Google
        authors = Group.objects.get(name='authors')  # получает объект группы с именем "common users"
        user.groups.add(authors)  # добавляет нового пользователя в группу

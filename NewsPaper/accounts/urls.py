from django.urls import path

from news.views import PostsList

urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем товарам у нас останется пустым, чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view. Для этого вызываем метод as_view.
   path('', PostsList.as_view(), name='posts'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения

]

# Теперь нам стали доступны новые пути:
#
#         accounts/login/ [name='login']
#         accounts/logout/ [name='logout']
#         accounts/password_change/ [name='password_change']
#         accounts/password_change/done/ [name='password_change_done']
#         accounts/password_reset/ [name='password_reset']
#         accounts/password_reset/done/ [name='password_reset_done']
#         accounts/reset/// [name='password_reset_confirm']accounts/reset/done/ [name='password_reset_complete']

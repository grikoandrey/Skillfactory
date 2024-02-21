from django.urls import path
# Импортируем созданное нами представление
from .views import PostsList, PostDetails, PostsSearch, PostCreate, PostEdit, PostDelete, ArticleCreate, ArticleEdit, \
   subscriptions

urlpatterns = [
   # path — означает путь.
   # В данном случае путь ко всем товарам у нас останется пустым, чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view. Для этого вызываем метод as_view.
   path('', PostsList.as_view(), name='posts'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', PostDetails.as_view(), name='post'),
   path('search/', PostsSearch.as_view(), name='posts_search'),
   path('news/create/', PostCreate.as_view(), name='news_create'),
   path('NEW/<int:pk>/edit/', PostEdit.as_view(), name='news_edit'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
   path('articles/create/', ArticleCreate.as_view(), name='articles_create'),
   path('ART/<int:pk>/edit/', ArticleEdit.as_view(), name='articles_edit'),
   # path('articles/<int:pk>/delete/', PostDelete.as_view(), name='articles_delete'),
   path('subscriptions/', subscriptions, name='subscriptions'),
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

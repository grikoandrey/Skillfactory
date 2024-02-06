# Импортируем необходимые модели и библиотеки
from django.contrib.auth.models import User
from news.models import Author, Category, Post, Comment

# Создаем двух пользователей
user1 = User.objects.create_user('user1')
user2 = User.objects.create_user('user2')

# Создаем два объекта модели Author, связанных с пользователями
author1 = Author.objects.create(author_user=user1)
author2 = Author.objects.create(author_user=user2)

# Добавляем 4 категории в модель Category
category1 = Category.objects.create(category='POL')
category2 = Category.objects.create(category='EDU')
category3 = Category.objects.create(category='SPR')
category4 = Category.objects.create(category='MUS')

# Добавляем 2 статьи и 1 новость
post1 = Post.objects.create(type_post='ART', title='Article 1', text='Content of Article 1', post_author=author1)
post2 = Post.objects.create(type_post='ART', title='Article 2', text='Content of Article 2', post_author=author2)
news1 = Post.objects.create(type_post='NEW', title='News 1', text='Content of News 1', post_author=author1)

# Присваиваем категории (как минимум в одной статье/новости должно быть не меньше 2 категорий)
post1.post_category.add(category1, category2)
post2.post_category.add(category3)
news1.post_category.add(category1, category4)

# Создаем как минимум 4 комментария к разным объектам модели Post
comment1 = Comment.objects.create(comment_text='Comment 1 for Post 1', comment_to_post=post1, comment_from_user=user1)
comment2 = Comment.objects.create(comment_text='Comment 2 for Post 2', comment_to_post=post2, comment_from_user=user2)
comment3 = Comment.objects.create(comment_text='Comment 3 for Post 1', comment_to_post=post1, comment_from_user=user2)
comment4 = Comment.objects.create(comment_text='Comment 4 for News 1', comment_to_post=news1, comment_from_user=user1)

# Применяем функции like() и dislike() к статьям/новостям и комментариям
post1.like()
post2.dislike()
comment1.like()
comment2.dislike()

# Обновляем рейтинги пользователей
author1.update_rating()
author2.update_rating()

# Выводим username и рейтинг лучшего пользователя
best_author = Author.objects.all().order_by('-author_rating').first()
print(f"Best User: {best_author.author_user.username}, Rating: {best_author.author_rating}")

# Выводим дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи
best_post = Post.objects.all().order_by('-post_rating').first()
print(f"Best Post - Date: {best_post.post_created_date}, Author: {best_post.post_author.author_user.username}, "
      f"Rating: {best_post.post_rating}, Title: {best_post.title}, Preview: {best_post.preview()}")

# Выводим все комментарии к этой статье
comments_to_best_post = Comment.objects.filter(comment_to_post=best_post)
for comment in comments_to_best_post:
    print(f"Date: {comment.comment_create_date}, User: {comment.comment_from_user.username}, "
          f"Rating: {comment.comment_rating}, Text: {comment.comment_text}")

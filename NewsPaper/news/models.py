from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.
class Author(models.Model):
    author_user = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг всех комментариев автора
        # comment_rating_sum = Comment.objects.filter(comment_from_user=self).aggregate(Sum('comment_rating'))[
        #                          'comment_rating__sum'] or 0
        # comment_rating_sum = self.author_user.comment_set.aggregate(com_rat=Sum('comment_rating'))
        # com_rat = 0
        # com_rat += comment_rating_sum.get('comment_rating')
        comment_rating_sum = self.author_user.comment_set.aggregate(com_rat=Sum('comment_rating')).get('com_rat', 0)

        # Суммарный рейтинг всех комментариев к статьям автора
        # post_rating_sum = Post.objects.filter(post_author=self).aggregate(Sum('post_rating'))['post_rating__sum'] or 0
        # post_rating_sum = self.post_set.aggregate(p_rating=Sum('post_rating'))
        # p_rat = 0
        # p_rat += post_rating_sum.get('post_rating')
        post_rating_sum = self.post_set.aggregate(p_rating=Sum('post_rating')).get('p_rating', 0)

        # Суммарный рейтинг каждой статьи автора умножается на 3
        self.author_rating = post_rating_sum * 3 + comment_rating_sum
        self.save()


class Category(models.Model):
    POLITICS, EDUCATION, SPORT, MUSIC = 'POL', 'EDU', 'SPR', 'MUS'

    SUBJECTS = [
        (POLITICS, 'политика'),
        (EDUCATION, 'образование'),
        (SPORT, 'спорт'),
        (MUSIC, 'музыка')
    ]
    category = models.CharField(max_length=3, choices=SUBJECTS, unique=True)


class Post(models.Model):
    ARTICLE, NEWS = 'ART', 'NEW'

    TYPE_POST = [(ARTICLE, 'Статья'), (NEWS, 'Новость')]

    type_post = models.CharField(max_length=3, choices=TYPE_POST, default=ARTICLE)
    title = models.CharField(max_length=50)
    text = models.TextField()
    post_created_date = models.DateTimeField(auto_now_add=True)
    post_rating = models.IntegerField(default=0)
    post_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_category = models.ManyToManyField(Category, through='PostCategory')

    def preview(self):
        return f"{self.text[:123]}..."

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_text = models.TextField()
    comment_create_date = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)
    comment_to_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_from_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()

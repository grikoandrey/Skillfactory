from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from news.models import Post, Subscriber, Category


@shared_task
def post_created(pk):
    instance = Post.objects.get(pk=pk)
    post_categories = instance.post_category.all()
    emails = User.objects.filter(subscriptions__category__in=post_categories).values_list('email', flat=True).distinct()

    categories_display = ", ".join(category.get_category_display() for category in post_categories)

    subject = f'Новая статья в категории {categories_display}'

    text_content = (
        f'Заголовок: {instance.title}\n'
        f'Содержание: {instance.text[0:15]}\n'
        f'Новая статья: {settings.SITE_URL}{instance.get_absolute_url()}'
    )
    html_content = (
        f'Заголовок: {instance.title}<br>'
        f'Содержание: {instance.text[0:15]}<br>'
        f'<a href="{settings.SITE_URL}{instance.get_absolute_url()}">Новая статья</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def weekly_send():
    last_week = timezone.now() - timedelta(days=1)
    new_posts = Post.objects.filter(post_created_date__gte=last_week).order_by('-post_created_date')
    subscribers_ids = Subscriber.objects.values_list('user_id', flat=True).distinct()

    for user_id in subscribers_ids:
        subscriber = Subscriber.objects.filter(user_id=user_id)
        category_ids = subscriber.values_list('category_id', flat=True)
        # Получаем время последней отправленной рассылки для данного подписчика
        last_notification_sent = subscriber.order_by('-last_notification_sent').first().last_notification_sent
        subscribed_categories = Category.objects.filter(id__in=category_ids)
        # Фильтруем новые статьи по времени и категориям пользователя
        new_posts_for_user = new_posts.filter(post_created_date__gte=last_notification_sent,
                                              post_category__in=subscribed_categories).distinct()
        # Если есть новые статьи для отправки
        if new_posts_for_user.exists():
            # Отправляем письмо
            email = subscriber.first().user.email
            html_content = render_to_string('weekly_mail.html',
                                            {'link': settings.SITE_URL, 'new_posts': new_posts_for_user})
            subject = 'Новые статьи в ваших подписанных категориях'
            msg = EmailMultiAlternatives(subject=subject, body='', from_email=None, to=[email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # Обновляем время последней отправленной рассылки для данного подписчика на текущее время
            subscriber.update(last_notification_sent=timezone.now())

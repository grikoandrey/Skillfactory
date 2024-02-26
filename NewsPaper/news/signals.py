# from django.contrib.auth.models import User
# from django.core.mail import EmailMultiAlternatives
# from django.db.models.signals import m2m_changed
# from django.dispatch import receiver

# from NewsPaper import settings
# from .models import PostCategory
# from .tasks import post_created


# @receiver(m2m_changed, sender=PostCategory)
# def new_post_created(instance, **kwargs):
#     if kwargs['action'] != 'post_add':
#         post_created.delay(instance.pk)

# @receiver(m2m_changed, sender=PostCategory)
# def post_created(instance, **kwargs):
#     if kwargs['action'] != 'post_add':
#         return
#     post_categories = instance.post_category.all()
#     emails = User.objects.filter(subscriptions__category__in=post_categories).
#     values_list('email', flat=True).distinct()
#
#     categories_display = ", ".join(category.get_category_display() for category in post_categories)
#
#     subject = f'Новая статья в категории {categories_display}'
#
#     text_content = (
#         f'Заголовок: {instance.title}\n'
#         f'Содержание: {instance.text[0:15]}\n'
#         f'Новая статья: {settings.SITE_URL}{instance.get_absolute_url()}'
#     )
#     html_content = (
#         f'Заголовок: {instance.title}<br>'
#         f'Содержание: {instance.text[0:15]}<br>'
#         f'<a href="{settings.SITE_URL}{instance.get_absolute_url()}">Новая статья</a>'
#     )
#     for email in emails:
#         msg = EmailMultiAlternatives(subject, text_content, None, [email])
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()

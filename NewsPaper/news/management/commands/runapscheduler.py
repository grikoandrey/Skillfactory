import logging
from datetime import timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Post, Subscriber, Category

logger = logging.getLogger(__name__)


def send_posts_emails():
    last_week = timezone.now() - timedelta(days=1)
    new_posts = Post.objects.filter(post_created_date__gte=last_week).order_by('-post_created_date')
    print(f'new_post: {new_posts}')
    categories = set(new_posts.values_list('post_category__category', flat=True))
    print(f'categories: {categories}')
    subscribers = set(Subscriber.objects.filter
                      (category__category__in=categories).values_list('user__email', flat=True))
    print(f'subscribers: {subscribers}')

    html_content = render_to_string(
        'weekly_mail.html',
        {'link': settings.SITE_URL, 'new_posts': new_posts, }
    )
    # Получаем читабельные наименования категорий
    categories_display = [Category.objects.get(category=category).get_category_display() for category in categories]
    # Объединяем их в строку для вставки в тему письма
    subject_categories = ", ".join(categories_display)
    subject = f'Статьи за неделю в категориях: {subject_categories}'
    for email in subscribers:
        msg = EmailMultiAlternatives(subject=subject, body='', from_email=None, to=[email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_posts_emails,
            trigger=CronTrigger(second='*/5'),  # day_of_week="fri", hour="18"
            id="send_posts_emails",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

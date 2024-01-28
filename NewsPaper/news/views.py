from django.views.generic import ListView, DetailView
from .models import Post


# Create your views here.
class PostsList(ListView):
    model = Post  # Указываем модель, объекты которой мы будем выводить
    # ordering = 'post_created_date'  # Поле, которое будет использоваться для сортировки объектов
    template_name = 'posts.html'  # Указываем имя шаблона, в котором будут все инструкции как показать
    context_object_name = 'posts'  # Это имя списка, в котором будут лежать все объекты.

    def get_queryset(self):
        return Post.objects.all().order_by('-post_created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_count'] = Post.objects.count()
        return context


class PostDetails(DetailView):
    model = Post  # Модель всё та же, но мы хотим получать информацию по отдельному товару
    template_name = 'post.html'  # Используем другой шаблон — post.html
    context_object_name = 'post'  # Название объекта, в котором будет выбранный пользователем продукт

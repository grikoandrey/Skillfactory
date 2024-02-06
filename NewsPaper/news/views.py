from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView

from .filters import PostFilter
from .models import Post
from .forms import PostsForm


# Create your views here.
class PostsList(ListView):
    model = Post  # Указываем модель, объекты которой мы будем выводить
    # ordering = 'post_created_date'  # Поле, которое будет использоваться для сортировки объектов
    template_name = 'posts.html'  # Указываем имя шаблона, в котором будут все инструкции как показать
    context_object_name = 'posts'  # Это имя списка, в котором будут лежать все объекты.
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # self.filterset = PostFilter(self.request.GET, queryset)
        return queryset.order_by('-post_created_date')
        # return Post.objects.all().order_by('-post_created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['filterset'] = self.filterset
        context['news_count'] = Post.objects.count()
        return context


class PostsSearch(ListView):
    model = Post  # Указываем модель, объекты которой мы будем выводить
    template_name = 'posts_search.html'  # Указываем имя шаблона, в котором будут все инструкции как показать
    context_object_name = 'posts'  # Это имя списка, в котором будут лежать все объекты.
    paginate_by = 5  # количество элементов на странице для пагинации

    def get_queryset(self):  # функция для возврата перечня постов в обратном порядке
        queryset = super().get_queryset()  # Получаем обычный запрос
        self.filterset = PostFilter(self.request.GET, queryset)  # Сохраняем нашу фильтрацию в объекте класса
        # return queryset.order_by('-post_created_date')
        return self.filterset.qs.order_by('-post_created_date')  # Возвращаем из функции отфильтрованный список товаров

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset  # Добавляем в контекст объект фильтрации.
        context['news_count'] = Post.objects.count()  # Добавляем в контекст количество постов.
        return context


class PostDetails(DetailView):
    model = Post  # Модель всё та же, но мы хотим получать информацию по отдельному посту
    template_name = 'post.html'  # Используем другой шаблон — post.html
    context_object_name = 'post'  # Название объекта, в котором будет выбранный пользователем пост


class PostCreate(CreateView):
    form_class = PostsForm  # Указываем нашу разработанную форму
    model = Post  # ссылаемся на модель поста
    template_name = 'news_create_edit.html'  # и новый шаблон, в котором используется форма.

    def form_valid(self, form):  # переопределяем зависимость создания категории от выбранной страницы
        news = form.save(commit=False)
        news.type_post = 'NEW'
        return super().form_valid(form)


class PostEdit(UpdateView):  # Представление для изменения новости.
    form_class = PostsForm
    model = Post
    template_name = 'news_edit.html'  # ссылка на свой шаблон


class PostDelete(DeleteView):  # Представление удаляющее новость.
    model = Post
    template_name = 'news_delete.html'  # ссылка на общий шаблон, так как удаление в принципе объекта
    success_url = reverse_lazy('posts')


class ArticleCreate(CreateView):
    form_class = PostsForm  # Указываем нашу разработанную форму
    model = Post  # ссылаемся на модель поста
    template_name = 'article_create.html'  # и новый шаблон, в котором используется форма.

    def form_valid(self, form):  # переопределяем зависимость создания категории от выбранной страницы
        news = form.save(commit=False)
        news.type_post = 'ART'
        return super().form_valid(form)


class ArticleEdit(UpdateView):  # Представление для изменения статьи.
    form_class = PostsForm
    model = Post
    template_name = 'article_edit.html'  # ссылка на свой шаблон

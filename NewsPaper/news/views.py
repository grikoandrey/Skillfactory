from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from .filters import PostFilter
from .models import Post, Author, Category, Subscriber
from .forms import PostsForm
from .tasks import post_created


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


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostsForm  # Указываем нашу разработанную форму
    model = Post  # ссылаемся на модель поста
    template_name = 'news_create_edit.html'  # и новый шаблон, в котором используется форма.

    def form_valid(self, form):  # переопределяем зависимость создания категории от выбранной страницы
        news = form.save(commit=False)
        news.type_post = 'NEW'
        author, created = Author.objects.get_or_create(author_user=self.request.user)
        form.instance.post_author = author
        news.save()  # сохранение поста
        post_created.delay(news.pk)  # и после сохранения вызов "таски"
        return super().form_valid(form)


class PostEdit(PermissionRequiredMixin, UpdateView):  # Представление для изменения новости.
    permission_required = ('news.change_post',)
    form_class = PostsForm
    model = Post
    template_name = 'news_edit.html'  # ссылка на свой шаблон

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект Post, который пользователь пытается редактировать
        post = self.get_object()
        # Проверяем, является ли текущий пользователь автором данного поста
        if request.user != post.post_author.author_user:
            return HttpResponseForbidden("Вы не можете изменять данную новость!")
        return super().dispatch(request, *args, **kwargs)


class PostDelete(PermissionRequiredMixin, DeleteView):  # Представление удаляющее новость.
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news_delete.html'  # ссылка на общий шаблон, так как удаление в принципе объекта
    success_url = reverse_lazy('posts')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostsForm  # Указываем нашу разработанную форму
    model = Post  # ссылаемся на модель поста
    template_name = 'article_create.html'  # и новый шаблон, в котором используется форма.

    def form_valid(self, form):  # переопределяем зависимость создания категории от выбранной страницы
        news = form.save(commit=False)
        news.type_post = 'ART'
        author, created = Author.objects.get_or_create(author_user=self.request.user)
        form.instance.post_author = author
        news.save()  # сохранение поста
        post_created.delay(news.pk)  # и после сохранения вызов "таски"
        return super().form_valid(form)


class ArticleEdit(PermissionRequiredMixin, UpdateView):  # Представление для изменения статьи.
    permission_required = ('news.change_post',)
    form_class = PostsForm
    model = Post
    template_name = 'article_edit.html'  # ссылка на свой шаблон

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.post_author.author_user:
            return HttpResponseForbidden("Вы не можете изменять данную статью!")
        return super().dispatch(request, *args, **kwargs)


@login_required
@csrf_protect
def subscriptions(request):
    is_authenticated = request.user.is_authenticated

    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscriber.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscriber.objects.filter(user=request.user, category=category, ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(Subscriber.objects.filter(user=request.user, category=OuterRef('pk'), ))
    ).order_by('category')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions, 'is_authenticated': is_authenticated}
    )

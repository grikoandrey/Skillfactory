from django_filters import FilterSet, CharFilter, DateFilter, ModelChoiceFilter
from django.forms.widgets import Select, DateInput
from .models import Post, Category


# Создаем свой набор фильтров для модели Post
# FilterSet, который мы наследуем, должен чем-то напомнить знакомые Django дженерики.
class PostFilter(FilterSet):
    title = CharFilter(    # перезадаем отображение окна фильтрации
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок'
    )

    post_category = ModelChoiceFilter(  # перезадаем отображение окна фильтрации. Данное с заданными параметрами
        field_name='post_category',
        queryset=Category.objects.all(),
        widget=Select(attrs={'class': 'form-control'}),
        label='Категория',
        empty_label='Выберите категорию',
    )

    post_created_date__lte = DateFilter(  # перезадаем отображение окна фильтрации.
        field_name='post_created_date',
        lookup_expr='lte',
        label='Дата (до)',
        widget=DateInput(attrs={'type': 'date'}),  # добавляем виджет для отображения календаря
    )

    post_created_date__gte = DateFilter(  # перезадаем отображение окна фильтрации.
        field_name='post_created_date',
        lookup_expr='gte',
        label='Дата (после)',
        widget=DateInput(attrs={'type': 'date'}),  # добавляем виджет для отображения календаря
    )

    class Meta:  # В Meta классе мы должны указать Django модель, в которой будем фильтровать записи.
        model = Post
        fields = {  # В fields мы описываем по каким полям модели будет производиться фильтрация.
                  'title': ['icontains'],
                  'post_category': ['exact'],
                  'post_created_date': ['lte', 'gte'],
                  # 'post_author': ['icontains'],
                  # 'type_post': [],
                  # 'text': ['icontains'],
                  # 'post_rating': ['lt', 'gt'],
                  }

    def __init__(self, *args, **kwargs):  # переопределение вывода категорий в читабельном виде
        super().__init__(*args, **kwargs)
        self.filters['post_category'].field.label_from_instance = lambda obj: obj.get_category_display()

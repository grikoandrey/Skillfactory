from django import forms
from django.core.exceptions import ValidationError

from .models import Post, Category


class PostsForm(forms.ModelForm):  # создали форму для работы с объектом Пост
    post_category = forms.ModelMultipleChoiceField(  # отдельно задали параметры для поля выбора
        queryset=Category.objects.all(),
        # widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        # widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
        label='Категория')
# to_field_name='id',  # Поле модели, которое будет использовано в качестве значения в выпадающем списке
# required=False,
# empty_label='Выберите категорию')  # Чтобы не добавлять "пустое" значение в начало списка

    class Meta:
        model = Post
        fields = [  # В fields мы описываем по каким полям модели будет производиться фильтрация, выборочно.
                  'title', 'post_category', 'text',  # 'post_author',
                  # 'post_created_date', # 'type_post', # 'post_rating',
                 ]
        labels = {  # задали читабельные наименования
            'title': 'Заголовок',
            'post_category': 'Категория',
            # 'post_author': 'Автор',
            'text': 'Текст',
        }

    def clean_title(self):  # добавили условие проверки
        title = self.cleaned_data["title"]
        if title and title[0].islower():
            raise ValidationError("Заголовок должен начинаться с заглавной буквы")
        return title

    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial['post_category'] = []  # Пустой список для начальных значений категорий
    #     return initial

    # def get_initial(self):
    #     initial = super().get_initial()
    #     if self.instance:  # Проверяем, что у формы есть экземпляр поста
    #         initial['post_category'] = self.instance.post_category.all()  # Получаем выбранные категории для поста
    #     return initial

    # def clean_post_author(self):
    #     author_name = self.cleaned_data['post_author']
    #     # Проверка существования автора в базе данных
    #     author, created = Author.objects.get_or_create(author_user__username=author_name)
    #     # Проверка правил валидации
    #     names = author_name.split()
    #     if len(names) < 2 or len(names) > 3 or any(name[0].islower() for name in names):
    #         raise ValidationError("Введите как минимум имя и фамилию с заглавной буквы.")
    #     return author

    def __init__(self, *args, **kwargs):  # переопределение вывода категорий в читабельном виде
        super().__init__(*args, **kwargs)
        self.fields['post_category'].label_from_instance = lambda obj: obj.get_category_display()
        # self.fields['post_author'].initial = 'Фамилия Имя'

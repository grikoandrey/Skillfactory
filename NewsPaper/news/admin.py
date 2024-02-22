from django.contrib import admin

from .models import Post, Category, PostCategory, Author, Comment, Subscriber


class CategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


class PostAdmin(admin.ModelAdmin):
    model = Post
    inlines = (CategoryInline,)


# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Comment)
admin.site.register(Subscriber)

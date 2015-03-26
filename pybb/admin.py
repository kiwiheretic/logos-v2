# -*- coding: utf-8
from django.contrib import admin

from pybb.models import Category, Forum, Topic, Post

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'position']


class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'position']


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'forum', 'created']


class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'created']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)

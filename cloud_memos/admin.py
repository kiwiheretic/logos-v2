from django.contrib import admin

# Register your models here.
from .models import Memo, Folder

@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    pass
    
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    pass
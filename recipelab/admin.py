from django.contrib import admin

from .models import Recipe, Version, ItemList

# Register your models here.

admin.site.register(Recipe)
admin.site.register(Version)
admin.site.register(ItemList)
# admin.site.register(Method)

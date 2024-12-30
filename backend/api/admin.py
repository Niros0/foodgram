from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import UserProfile
from recipes.models import Tag, Ingredient


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    list_filter = ['name']

class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    list_filter = ['name']


admin.site.register(UserProfile, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
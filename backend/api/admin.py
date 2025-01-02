from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import UserProfile, Subscriptions
from recipes.models import Tag, Ingredient, Favorites, Recipe, ShoppingCart


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    list_filter = ['name']


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    list_filter = ['name']


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = [
        'author__username', 'author__email',
        'user__username', 'user__email'
    ]
    list_filter = ['author__username', 'user__username']


class RecipesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author', 'favorites']
    search_fields = ['name', 'author__username']
    list_filter = ['tags', 'author', 'name']
    inlines = (IngredientsInLine,)

    def favorites(self, obj):
        return Favorites.objects.filter(recipe=obj).count()

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']


admin.site.register(UserProfile, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Subscriptions, SubscribeAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Favorites, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
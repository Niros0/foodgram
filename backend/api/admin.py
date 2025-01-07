from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import UserProfile, Subscriptions
from recipes.models import (
    Tag,
    Ingredient,
    Favorites,
    Recipe,
    ShoppingCart,
    AmountIngredient
)


class IngredientsInLine(admin.TabularInline):
    """
    Встроенный класс для отображения ингредиентов рецепта в админке.

    Этот класс позволяет отображать список ингредиентов рецепта.
    """
    model = Recipe.ingredients.through


class TagAdmin(admin.ModelAdmin):
    """ 
    Класс администратора для модели Tag.

    Этот класс настраивает интерфейс администратора для управления тегами.
    Он позволяет администраторам добавлять, изменять и удалять теги.
    """
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    list_filter = ['name']


class IngredientAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Ingredient.

    Этот класс предоставляет интерфейс для управления ингредиентами.
    Он включает функции для поиска и фильтрации
    ингредиентов по имени и единице измерения.
    """
    list_display = ['name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    list_filter = ['name']


class SubscribeAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Subscriptions.

    Этот класс позволяет управлять подписками пользователей на рецепты.
    Он включает поиск по автору рецепта и пользователю.
    """
    list_display = ['user', 'author']
    search_fields = [
        'author__username', 'author__email',
        'user__username', 'user__email'
    ]
    list_filter = ['author__username', 'user__username']


class RecipesAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Recipe.

    Этот класс настраивает интерфейс администратора для управления рецептами.
    Он позволяет администраторам добавлять, изменять и удалять рецепты, 
    а также управлять ингредиентами рецепта.
    """
    list_display = ['id', 'name', 'author', 'favorites']
    search_fields = ['name', 'author__username']
    list_filter = ['tags', 'author', 'name']
    inlines = (IngredientsInLine,)

    def favorites(self, obj):
        """
        Метод для отображения количества добавлений рецепта в избранное.

        Возвращает количество объектов Favorites, связанных с рецептом.
        """
        return Favorites.objects.filter(recipe=obj).count()


class FavoriteAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели Favorites.

    Этот класс предоставляет интерфейс для управления избранными рецептами.
    Он включает отображение идентификатора, пользователя и рецепта.
    """
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели ShoppingCart.

    Этот класс позволяет управлять корзиной покупок пользователей.
    Он включает отображение идентификатора пользователя и рецепта.
    """
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user__username', 'user__email']


class AmountIngredientAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели AmountIngredientAdmin.
    """
    list_display = ('recipe', 'ingredients', 'amount')
    search_fields = ('recipe__name', 'ingredients__name')
    list_filter = ('recipe', 'ingredients')


admin.site.register(AmountIngredient, AmountIngredientAdmin)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Subscriptions, SubscribeAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(Favorites, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

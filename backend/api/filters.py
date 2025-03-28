from django_filters import rest_framework as filter
from django_filters import CharFilter, FilterSet

from recipes.models import Recipe, Tag, Ingredient
from users.models import User


class RecipeFilter(filter.FilterSet):
    """
    Класс фильтров для рецептов.
    """
    author = filter.ModelChoiceFilter(
        queryset=User.objects.all(),
        to_field_name="id",
    )
    tags = filter.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = filter.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filter.BooleanFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=self.request.user)
            return queryset.exclude(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(shoppinga_cart__user=self.request.user)
            return queryset.exclude(shoppinga_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ("name",)

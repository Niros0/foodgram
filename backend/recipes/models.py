from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from shortener.models import UrlMap

from users.models import User
from recipes.constants import (
    MAX_NAME_LENGTH,
    MAX_MEASUREMET_LENGTH,
    MIN_AMOUNT,
    MAX_AMOUNT
)


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название ингредиента",
        help_text="Введите название ингредиента",
        unique=True
    )

    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMET_LENGTH,
        verbose_name="Единица измерения",
        help_text="Введите единицу измерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название тега",
        help_text="Введите название тега",
        unique=True
    )

    slug = models.SlugField(
        verbose_name="Slug тега",
        help_text="Введите slug тега",
        unique=True
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text="Выберите автора рецепта"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Название рецепта",
        help_text="Введите название рецепта",
    )

    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Картинка рецепта",
        help_text="Загрузите изображение рецепта",
    )

    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Введите описание рецепта",
    )

    ingredients = models.ManyToManyField(
        verbose_name="Ингредиенты блюда",
        related_name="recipes",
        to=Ingredient,
        through="AmountIngredient",
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
        help_text="Выберите теги для рецепта",
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                "Укажите время приготовления!"
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                "Время приготовления не должно превышать 32 000 минут!"
            )
        ],
    )

    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )

    short_link = models.OneToOneField(
        UrlMap,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class Favorites(models.Model):
    """Избранные рецепты."""

    recipe = models.ForeignKey(
        verbose_name="Понравившиеся рецепты",
        related_name="favorites",
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Пользователь",
        related_name="favorites",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ["user"]
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorites"
            ),
        )

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCart(models.Model):
    """Модель корзины"""

    recipe = models.ForeignKey(
        verbose_name="Рецепты в списке покупок",
        related_name="shoppinga_cart",
        to=Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Владелец списка",
        related_name="shoppinga_cart",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        ordering = ["-id"]
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unique_shopping_cart",
            ),
        )

    def __str__(self):
        return f"{self.user} {self.recipe}"


class AmountIngredient(models.Model):
    """Количество ингридиентов в блюде."""

    recipe = models.ForeignKey(
        verbose_name="В каких рецептах",
        related_name="recipe_ingredients",
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        verbose_name="Связанные ингредиенты",
        related_name="ingredient_recipes",
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество ингредиентов",
        default=0,
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                "Количество ингредиентов должно быть не менее 1!"
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                "Количество ингредиентов не должно превышать 32 000!"
            )
        ],
    )

    class Meta:
        verbose_name = "Ингредиенты"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe",)
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredients"], name="ingredient_recipe"
            )
        ]

    def __str__(self):
        return f"{self.amount} {self.ingredients}"

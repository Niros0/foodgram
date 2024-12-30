from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField(
        max_length=255,
        verbose_name="Название ингредиента",
        help_text="Введите название ингредиента",
        unique=True
    )

    measurement_unit = models.CharField(
        max_length=255,
        verbose_name="Единица измерения",
        help_text="Введите единицу измерения"
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField(
        max_length=255,
        verbose_name="Название тега",
        help_text="Введите название тега",
        unique=True
    )

    slug = models.SlugField(
        verbose_name="Slug тега",
        help_text="Введите slug тега",
        unique=True
    )

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
        help_text="Введите название рецепта"
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name="Картинка рецепта",
        help_text="Загрузите изображение рецепта"
    )

    text = models.TextField(
        verbose_name="Описание рецепта",
        help_text="Введите описание рецепта"
    )

    ingredients = models.ManyToManyField(
        verbose_name="Ингредиенты блюда",
        related_name="recipes",
        to=Ingredient,
        through="recipes.AmountIngredient",
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
        help_text="Выберите теги для рецепта"
    )

    cooking_time = models.IntegerField(
        verbose_name="Время приготовления",
        help_text="Введите время приготовления в минутах"
    )
    short_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Короткая ссылка",
        help_text="Короткая ссылка на рецепт"
    )

    def __str__(self):
        return self.name


class Favorites(models.Model):
    """Избранные рецепты."""

    recipe = models.ForeignKey(
        verbose_name="Понравившиеся рецепты",
        related_name="in_favorites",
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

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCart(models.Model):

    recipe = models.ForeignKey(
        verbose_name="Рецепты в списке покупок",
        related_name="is_in_shoppinga_cart",
        to=Recipe,
        on_delete=models.CASCADE,
        default=None
    )
    user = models.ForeignKey(
        verbose_name="Владелец списка",
        related_name="carts",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"

    def __str__(self):
        return f"{self.user} {self.recipe}"


class AmountIngredient(models.Model):
    """Количество ингридиентов в блюде."""

    recipe = models.ForeignKey(
        verbose_name="В каких рецептах",
        related_name="ingredient",
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        verbose_name="Связанные ингредиенты",
        related_name="recipe",
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Количество ингридиентов"
        ordering = ("recipe",)

    def __str__(self):
        return f"{self.amount} {self.ingredients}"

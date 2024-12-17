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

    unit = models.CharField(
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
        Ingredient,
        verbose_name="Ингредиенты",
        help_text="Выберите ингредиенты для рецепта"
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
    is_favorited = models.BooleanField(
        default=False,
        verbose_name="Добавлен в избранное",
        help_text="Указывает, добавил ли текущий пользователь рецепт в избранное"
    )
    short_link = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Короткая ссылка",
        help_text="Короткая ссылка на рецепт"
    )

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    '''Модель корзины'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Выберите пользователя"
    )

    recipes = models.ManyToManyField(
        Recipe,
        verbose_name="Рецепты",
        help_text="Выберите рецепты для корзины"
    )

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

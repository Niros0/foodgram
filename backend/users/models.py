from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from .constants import (
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_FIRSTNAME_LENGTH,
    MAX_LASTNAME_LENGTH,
)


class UserProfile(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        verbose_name="Юзернейм",
        help_text="Введите юзернейм пользователя (максимум 150 символов).",
        validators=[UnicodeUsernameValidator()],
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта пользователя",
        help_text="Введите свою почту",
        max_length=MAX_EMAIL_LENGTH,
    )

    first_name = models.CharField(
        verbose_name="Имя пользователя",
        help_text="Введите свое имя",
        max_length=MAX_FIRSTNAME_LENGTH,
    )

    last_name = models.CharField(
        verbose_name="Фамилия пользователя",
        help_text="Введите свою фамилию",
        max_length=MAX_LASTNAME_LENGTH,
    )

    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name="Аватар пользователя",
        help_text="Загрузите изображение аватара пользователя"
    )

    password = models.CharField(
        verbose_name=("Пароль"),
        max_length=128,
        help_text='Напишите пароль',
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return f"{self.username}: {self.email}"
    
    @property
    def is_admin(self):
        return self.is_superuser or self.is_staff


class Subscriptions(models.Model):
    """Подписки пользователей друг на друга."""

    author = models.ForeignKey(
        verbose_name="Автор рецепта",
        related_name="subscribers",
        to=UserProfile,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Подписчик",
        related_name="subscriptions",
        to=UserProfile,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"],
                name="subscriptions_unique",
            )
        ]

    def __str__(self):
        return f"{self.user.username} {self.author.username}"


User = get_user_model()

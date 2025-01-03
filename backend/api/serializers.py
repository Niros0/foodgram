from users.models import User, Subscriptions
from recipes.models import Tag, Ingredient, Recipe, Favorites, ShoppingCart, AmountIngredient
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from shortener.models import UrlMap
from shortener.shortener import create
from django.urls import reverse
from django.http import request
from collections.abc import Hashable

class BaseSerializer(serializers.ModelSerializer):
    """Базовый класс для валидации пустых и повторяющихся значений."""

    def validate_non_empty_list(self, field_name, value):
        if not value:
            raise serializers.ValidationError(f"Поле {field_name} не должно быть пустым.")
        unique_values = set()
        for item in value:
            if isinstance(item, Hashable):
                if item in unique_values:
                    raise serializers.ValidationError(f"Поле {field_name} содержит повторяющиеся элементы!")
                unique_values.add(item)
        return value
    
class UserCreateSerializer(ModelSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(ModelSerializer):
    """Сериализатор для работы с пользователями."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            'avatar',
            "is_subscribed",
        )
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        """Подписан ли пользователь на данного автора."""
        user = self.context.get("request").user
        return user.is_authenticated and user.subscriptions.filter(author=obj).exists()


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        print(instance.avatar)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class TagsSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов с ингредиентами."""

    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = AmountIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="recipe_ingredients"
    )
    is_favorited = serializers.ReadOnlyField(read_only=True, default=False)
    is_in_shopping_cart = serializers.ReadOnlyField(
        read_only=True, default=False
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class IngredientRecipeCreateSerializer(serializers.Serializer):
    """Сериализатор добавления ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "Количество ингредиента должно быть не менее 1."
        },
    )


class RecipeCreateSerializer(BaseSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    ingredients = IngredientRecipeCreateSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        return self.validate_non_empty_list('ingredients', value)

    def validate_tags(self, value):
        return self.validate_non_empty_list('tags', value)
    
    def validate_image(self, value):
        return self.validate_non_empty_list('image', value)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """Добавление ингредиентов в рецепт."""
        try:
            AmountIngredient.objects.bulk_create(
                AmountIngredient(
                    recipe=recipe,
                    ingredients_id=ingredient["id"],
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            )
        except Exception as e:
            raise serializers.ValidationError(f"Ингридиенты не найдены: {e}")
        
    def create(self, validated_data: dict):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        short_link = create(user=author, link=reverse("api:recipes-detail", args=[recipe.id]))
        recipe.short_link = UrlMap.objects.get(short_url=short_link)
        recipe.save()
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is None:
            raise serializers.ValidationError("Поле `ingredients` обязательно для обновления.")
        if tags is None:
            raise serializers.ValidationError("Поле `tags` обязательно для обновления.")
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="recipe.id", read_only=True)
    name = serializers.ReadOnlyField(source="recipe.name")
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    image = Base64ImageField(read_only=True, source="recipe.image")

    class Meta:
        model = Favorites
        fields = ("id", "name", "image", "cooking_time", "recipe", "user")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                fields=["recipe", "user"],
                message="Рецепт уже находится в избранных",
            )
        ]
        extra_kwargs = {
            "recipe": {"write_only": True},
            "user": {"write_only": True},
        }


class ShoppingSerializer(FavoriteSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time", "recipe", "user")
        extra_kwargs = {
            "recipe": {"write_only": True},
            "user": {"write_only": True},
        }


class RecipeForSubscribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = RecipeForSubscribeSerializer(
        many=True, source="author.recipes", read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "recipes",
            "user",
            "author",
            "is_subscribed",
            "recipes_count",
            "avatar",
        )
        extra_kwargs = {
            "author": {"write_only": True},
            "user": {"write_only": True},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=("author", "user"),
                message="Вы уже подписаны на данного автора",
            )
        ]

    def get_avatar(self, obj):
        if obj.author.avatar:
            return obj.author.avatar.url
        else:
            return None

    def validate(self, attrs):
        author = attrs["author"]
        user = attrs["user"]
        if author == user:
            raise serializers.ValidationError(
                "Вы не можете подписаться на самого себя."
            )
        return super().validate(attrs)

    def get_is_subscribed(self, obj):
        """Подписан ли пользователь на данного автора."""
        user = self.context.get("request").user
        return user.is_authenticated and obj.user_id == user.id

    def to_representation(self, instance):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit", 0)
        data = super().to_representation(instance)
        if limit and limit.isdigit():
            data["recipes"] = data["recipes"][:int(limit)]
        recipes_count = instance.author.recipes.count()
        data["recipes_count"] = recipes_count
        return data


class RecipeLinkSerializer(serializers.Serializer):
    short_link = serializers.SerializerMethodField()

    class Meta:
        fields = ('short_link',)

    def get_short_link(self, obj):
        if obj.short_link:
            domain = self.context.get('domain')
            return f"https://{domain}/s/{obj.short_link.short_url}"
        return None
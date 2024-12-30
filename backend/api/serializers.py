from users.models import User
from recipes.models import Tag, Ingredient, Recipe, Favorites, ShoppingCart
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

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

        user = self.context.get("request").user

        if user.is_anonymous or (user == obj):
            return False

        return user.subscriptions.filter(author=obj).exists()


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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

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
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        return IngredientSerializer(ingredients, many=True, context=self.context).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return obj.shopping_cart.filter(user=user).exists()

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not ingredients or not tags:
            raise serializers.ValidationError("Ingredients and tags are required")
        return data



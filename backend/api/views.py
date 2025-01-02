from rest_framework import viewsets
from api.mixins import ModelMixinSet
from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorites
from djoser.views import UserViewSet as DjoserUserViewSet
from api.pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from api.permissions import IsAuthOwner, IsAuthAdminAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer, 
    TagsSerializer, 
    IngredientSerializer, 
    RecipeCreateSerializer, 
    RecipeSerializer,
    ShoppingSerializer,
    FavoriteSerializer,
    SubscribeSerializer,
    RecipeLinkSerializer
)
from users.models import User, Subscriptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Exists, OuterRef, Sum, Count
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .filters import RecipeFilter
from django.http import HttpResponse
from django.urls import reverse
from django.http import JsonResponse
import random
import string
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer

class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthAdminAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # queryset = queryset.annotate()
        if self.request.user.is_authenticated:
            is_in_shopping_cart_subquery = Exists(
                ShoppingCart.objects.filter(
                    recipe_id=OuterRef("id"), user=self.request.user
                )
            ) 
            queryset = queryset.annotate(
                is_in_shopping_cart=is_in_shopping_cart_subquery
            )
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorites.objects.filter(
                        recipe_id=OuterRef("id"), user=self.request.user
                    )
                )
            )
        queryset = queryset.select_related("author")
        queryset = queryset.prefetch_related("recipe_ingredients", "tags")
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return self.serializer_class

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Избранные рецепты."""
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={"recipe": recipe.id, "user": user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Favorites, recipe=recipe, user=user).delete()
        return Response(
            {"message": "Рецепт удален из избранных"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Список покупок."""
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            serializer = ShoppingSerializer(
                data={"recipe": recipe.id, "user": user.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(ShoppingCart, recipe=recipe, user=user).delete()
        return Response(
            {"message": "Рецепт удален из списка покупок"},
            status=status.HTTP_204_NO_CONTENT,
        )


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',) 


class UserViewSet(DjoserUserViewSet):
    pagination_class = CustomPageNumberPagination

    @action(detail=False,
            methods=['get', 'patch', ],
            permission_classes=(IsAuthOwner,))
    def me(self, request):
        """
        Позволяет пользователю получить или обновить свои данные.
        Доступно только для аутентифицированных пользователей.
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        """Создание и удаление подписки на автора."""
        user = request.user
        if request.method == "POST":
            serializer = SubscribeSerializer(
                data={"user": user.id, "author": id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscriptions, user=user, author__id=id
        ).delete()
        return Response(
            {"message": "Подписка удалена"}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок на авторов."""
        user = request.user
        subscribe = (
            Subscriptions.objects.filter(user=user)
            .prefetch_related("author__recipes")
            .annotate(recipes_count=Count("author__recipes"))
        ).order_by("author__email")
        page = self.paginate_queryset(subscribe)
        serializer = SubscribeSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

class AvatarView(APIView):
    permission_classes = [IsAuthOwner]
    serializer_class = AvatarSerializer

    def put(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            user.save()
            return Response({'avatar': request.build_absolute_uri(user.avatar.url)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = User.objects.get(pk=request.user.pk)
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RecipeLinkView(APIView):
    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        domain = request.get_host()
        serializer = RecipeLinkSerializer(recipe, context={'domain': domain})
        return Response(serializer.data)
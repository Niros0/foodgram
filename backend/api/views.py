from rest_framework import viewsets, filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.db.models import Exists, OuterRef, Sum, Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.conf import settings

from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    ShoppingCart,
    Favorites,
    AmountIngredient
)
from api.pagination import CustomPageNumberPagination
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
from .filters import RecipeFilter


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
        if self.request.user.is_authenticated:
            is_in_shopping_cart_subquery = Exists(
                ShoppingCart.objects.filter(
                    recipe_id=OuterRef("id"), user=self.request.user
                )
            )
            is_favorited_subquery = Exists(
                Favorites.objects.filter(
                    recipe_id=OuterRef("id"), user=self.request.user
                )
            )
            queryset = queryset.annotate(
                is_in_shopping_cart=is_in_shopping_cart_subquery,
                is_favorited=is_favorited_subquery,
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
        try:
            favor = Favorites.objects.get(recipe=recipe, user=user)
            favor.delete()
            return Response(
                {"message": "Рецепт удален из избранных"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Favorites.DoesNotExist:
            return HttpResponseBadRequest("Рецепт не найден в избранных.")

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == "POST":
            serializer = ShoppingSerializer(
                data={"recipe": recipe.id, "user": user.id}
            )
            serializer.is_valid(raise_exception=True)
            if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
                return Response(
                    {"message": "Рецепт уже в корзине."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        try:
            cart = ShoppingCart.objects.get(recipe=recipe, user=user)
            cart.delete()
            return Response({"message": "Рецепт удален из списка покупок"},
                            status=status.HTTP_204_NO_CONTENT,
                            )
        except ShoppingCart.DoesNotExist:
            return HttpResponseBadRequest("Рецепт не найден в корзине.")

    @action(
        methods=("get",),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        ingredients = (
            AmountIngredient.objects.filter(
                recipe__shoppinga_cart__user=request.user)
            .values("ingredients__name", "ingredients__measurement_unit")
            .annotate(sum_amount=Sum("amount"))
        )

        html = render_to_string(
            "shopping_cart.html",
            {"ingredients": ingredients}
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=shortlist.pdf"
        HTML(string=html).write_pdf(response, stylesheets=[
            CSS(f"{settings.STATICFILES_DIRS[0]}/css/pdf.css")])

        return response


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
            get_object_or_404(User, id=id)
            serializer = SubscribeSerializer(
                data={"user": user.id, "author": id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            get_object_or_404(User, id=id)
            subscription = Subscriptions.objects.get(user=user, author__id=id)
            subscription.delete()
            return Response(
                {"message": "Подписка удалена"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Subscriptions.DoesNotExist:
            return HttpResponseBadRequest("Subscription does not exist.")

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,)
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
            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )
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
        full_url = request.build_absolute_uri()
        base_url = '/'.join(full_url.split('/')[:-5])
        serializer = RecipeLinkSerializer(
            recipe,
            context={'base_url': base_url}
        )
        return Response(serializer.data)

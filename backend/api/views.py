from rest_framework import viewsets
from api.mixins import ModelMixinSet
from recipes.models import Tag, Recipe, Ingredient
from djoser.views import UserViewSet as DjoserUserViewSet
from api.pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from api.permissions import IsAuthOwner, IsAuthAdminAuthorOrReadOnly
from api.serializers import AvatarSerializer, TagsSerializer, IngredientSerializer, RecipeSerializer
from users.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer



class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthAdminAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('is_favorited', 'author', 'tags')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',) 


class UserViewSet(DjoserUserViewSet):
    pagination_class = CustomPageNumberPagination

    @action(detail=False,
            methods=['get',],
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
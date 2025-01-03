from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagsViewSet,
    UserViewSet,
    AvatarView,
    RecipeLinkView,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"


router = DefaultRouter()
router.register(r"tags", TagsViewSet, "tags")
router.register(r"ingredients", IngredientViewSet, "ingredients")
router.register(r"recipes", RecipeViewSet, "recipes")
router.register(r"users", UserViewSet)

urlpatterns = (
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path('recipes/<int:pk>/get-link/', RecipeLinkView.as_view(), name='get_recipe_link'),
)


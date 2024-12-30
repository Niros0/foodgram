from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagsViewSet,
    UserViewSet,
    AvatarView,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"


router = DefaultRouter()
router.register("tags", TagsViewSet, "tags")
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register(r"users", UserViewSet)

urlpatterns = (
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
)
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet
from rest_framework import  permissions


class ModelMixinSet(ListModelMixin, GenericViewSet):
    pass
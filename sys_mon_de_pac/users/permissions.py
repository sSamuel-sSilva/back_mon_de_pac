from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class ActionPermission(BasePermission):
    actions = {
        "list": "list",
        "retrieve": "retrieve",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        model = view.queryset.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        perm_codename = self.actions.get(view.action)
        if not perm_codename:
            return False
        
        full_perm = f"{app_label}.{perm_codename}_{model_name}"
        return user.has_perm(full_perm)
    

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return True

from rest_framework.permissions import BasePermission


class ERPModelPermissions(BasePermission):

    def has_permission(self, request, view):
        action = getattr(view, 'action', None)
        model = view.queryset.model

        if action == 'confirm':
            return request.user.has_perm(
                f'{model._meta.app_label}.confirm_{model._meta.model_name}'
            )

        if action == 'cancel':
            return request.user.has_perm(
                f'{model._meta.app_label}.cancel_{model._meta.model_name}'
            )

        permission_map = {
            'GET': 'view',
            'HEAD': 'view',
            'OPTIONS': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
        }

        permission = permission_map.get(request.method)

        if permission is None:
            return False

        return request.user.has_perm(
            f'{model._meta.app_label}.{permission}_{model._meta.model_name}'
        )
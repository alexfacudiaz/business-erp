from rest_framework.permissions import DjangoModelPermissions


class ERPModelPermissions(DjangoModelPermissions):

    def has_permission(self, request, view):
        action = getattr(view, 'action', None)

        if action in (
            'confirm',
            'cancel',
            'activate',
            'deactivate',
        ):
            model = view.queryset.model

            return request.user.has_perm(
                f'{model._meta.app_label}.{action}_{model._meta.model_name}'
            )

        return super().has_permission(request, view)
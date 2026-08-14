from django.contrib import admin
from .models import Customer

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'customer_type',
        'tax_id',
        'email',
        'is_active'
    )

    list_filter = (
        'customer_type',
        'is_active'
    )

    search_fields = (
        'first_name',
        'last_name',
        'business_name',
        'tax_id',
        'email'
    )

    ordering = (
        'customer_type',
        'last_name',
        'business_name'
    )

    @admin.display(description='Name')
    def display_name(self, obj):
        return str(obj)

    @admin.action(description='Activar clientes seleccionados')
    def activate_customers(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Desactivar clientes seleccionados')
    def deactivate_customers(self, request, queryset):
        queryset.update(is_active=False)

    actions = (
        'activate_customers',
        'deactivate_customers'
    )


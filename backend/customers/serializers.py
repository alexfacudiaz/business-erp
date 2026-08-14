from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = (
            'id',
            'customer_type',
            'tax_id',
            'first_name',
            'last_name',
            'business_name',
            'email',
            'phone',
            'address',
            'notes',
            'is_active',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at'
        )

    def validate(self, attrs):
        customer_type = attrs.get(
            'customer_type',
            getattr(self.instance, 'customer_type', None)
        )

        first_name = attrs.get(
            'first_name',
            getattr(self.instance, 'first_name', None)
        )

        last_name = attrs.get(
            'last_name',
            getattr(self.instance, 'last_name', None)
        )

        business_name = attrs.get(
            'business_name',
            getattr(self.instance, 'business_name', None)
        )

        if customer_type == Customer.CustomerType.PERSON:
            if not first_name:
                raise serializers.ValidationError({
                    'first_name': 'Las personas deben tener nombre.'
                })

            if not last_name:
                raise serializers.ValidationError({
                    'last_name': 'Las personas deben tener apellido.'
                })

            if business_name:
                raise serializers.ValidationError({
                    'business_name': (
                        'Las personas no deben tener razón social.'
                    )
                })

        elif customer_type == Customer.CustomerType.COMPANY:
            if not business_name:
                raise serializers.ValidationError({
                    'business_name': (
                        'Las empresas deben tener razón social.'
                    )
                })

            if first_name or last_name:
                raise serializers.ValidationError({
                    'first_name': (
                        'Las empresas no deben tener nombre o apellido.'
                    ),
                    'last_name': (
                        'Las empresas no deben tener nombre o apellido.'
                    ),
                })

        return attrs
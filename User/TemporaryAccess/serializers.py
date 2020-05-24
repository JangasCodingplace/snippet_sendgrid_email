from rest_framework import serializers

from .models import TemporaryAccess

class TemporaryAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryAccess
        fields = (
            'user',
            'group'
        )

    def create(self, validated_data):
        if validated_data['group'] == 'pw':
            return TemporaryAccess.objects.create_password_forgotten_access(**validated_data)
        elif validated_data['group'] == 'l':
            return TemporaryAccess.objects.create_login_access(**validated_data)
        else:
            raise ValueError('Activation Key can not get created at this point!')

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
        )
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
        }

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )
from django.contrib.auth import authenticate
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializers(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "username", "bio", "is_verified")

class UploadProfileImageSerializer(Serializer):

      profile_image = serializers.ImageField()

      def update(self, instance, validated_data):
          instance.profile_image = validated_data.get('profile_image', instance.profile_image)
          instance.save()
          return instance

class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginUserSerializer(Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect credentials")

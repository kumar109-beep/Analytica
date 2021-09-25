from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        chartconfig = Chartconfig.objects.create(**validated_data)
        print(chartconfig)
        print("==="*30)
        return chartconfig

    def update(self, instance, validated_data):
        pass


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        chartconfig = Chartconfig.objects.create(**validated_data)
        print(chartconfig)
        print("==="*30)
        return chartconfig

    def update(self, instance, validated_data):
        pass


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

    def create(self, validated_data):
        chartconfig = Chartconfig.objects.create(**validated_data)
        print(chartconfig)
        print("==="*30)
        return chartconfig

    def update(self, instance, validated_data):
        pass
        
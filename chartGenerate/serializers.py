from django.contrib.auth.models import User, Group
from . models import Chartconfig
from rest_framework import serializers

class ChartconfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chartconfig
        fields = '__all__'

    def create(self, validated_data):
        chartconfig = Chartconfig.objects.create(**validated_data)
        print(chartconfig)
        print("==="*30)
        return chartconfig

    def update(self, instance, validated_data):
        pass
        # albums_data = validated_data.pop('album_musician')
        # albums = (instance.album_musician).all()
        # albums = list(albums)
        # instance.first_name = validated_data.get('first_name', instance.first_name)
        # instance.last_name = validated_data.get('last_name', instance.last_name)
        # instance.instrument = validated_data.get('instrument', instance.instrument)
        # instance.save()

        # for album_data in albums_data:
        #     album = albums.pop(0)
        #     album.name = album_data.get('name', album.name)
        #     album.release_date = album_data.get('release_date', album.release_date)
        #     album.num_stars = album_data.get('num_stars', album.num_stars)
        #     album.save()
        # return instance
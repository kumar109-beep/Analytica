from django.contrib.auth.models import User, Group
from . models import Dataframe, Frame_edit_request
from rest_framework import serializers


class DataframeSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        request = kwargs.get('context', {}).get('request')
        str_fields = request.GET.get('fields', '') if request else None
        fields = str_fields.split(',') if str_fields else None    # Instantiate the superclass normally
        super(DataframeSerializer, self).__init__(*args, **kwargs)    
        if fields is not None:
            # Drop any fields that are not specified in the `fields`
            # argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Dataframe
        fields = '__all__'
        # fields = ['id']
        
    def create(self, validated_data):
        dataframe = Dataframe.objects.create(**validated_data)
        print(dataframe)
        print("==="*30)
        return dataframe

    def update(self, instance, validated_data):
        pass


class CustomForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return Dataframe.objects.filter(id=2)

# class UserPhotoForeignKey(serializers.PrimaryKeyRelatedField):
#     def get_queryset(self):
#         return Image.objects.filter(owner=self.context['request'].user)
        

class Frame_edit_requestSerializer(serializers.ModelSerializer):
    # frame = CustomForeignKey()
    class Meta:
        model = Frame_edit_request
        fields = '__all__'
        # read_only_fields = ('id', 'hash_code')

    def create(self, validated_data):
        frame_request_edit = Frame_edit_request.objects.create(**validated_data)
        return frame_request_edit

    def update(self, instance, validated_data):
        instance.verified = validated_data.get('verified', instance.verified)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance


    def get_or_create(self, validated_data):
        print("danish"*300)
        defaults = self.validated_data.copy()
        identifier = defaults.pop('unique_field')
        return MyObject.objects.get_or_create(unique_field=identifier, defaults=defaults)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from abstract.serializers import AbstractSerializer
from user.models import User
from user.serializers import UserSerializer
from .models import Post


class PostSerializer(AbstractSerializer):
    author = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='public_id')
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    def validate_author(self, value):
        if self.context['request'].user != value:
            raise ValidationError("You can't create a post for another user.")

        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        author = User.objects.get_object_by_public_id(rep['author'])
        rep['author'] = UserSerializer(author, context=self.context).data

        return rep

    def update(self, instance, validated_data):
        if not instance.edited:
            validated_data['edited'] = True

        instance = super().update(instance, validated_data)
        return instance

    def get_liked(self, instance):
        request = self.context.get('request', None)

        if request is None or request.user.is_anonymous:
            return False

        return request.user.has_liked(instance)

    def get_likes_count(self, instance):
        return instance.liked_by.count()

    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'body',
            'edited',
            'liked',
            'likes_count',
            'created',
            'updated'
        )
        read_only_fields = ('edited',)

from rest_framework import serializers
from .models import Messages, UserProfile


class MessageSerializer(serializers.ModelSerializer):
    """
    This class is a serializer for the Messages model.
    It includes 'sender_name' and 'receiver_name' fields, which are SlugRelatedFields that map to the 'username' field of the UserProfile model.
    It also includes 'description' and 'time' fields from the Messages model.

    :inherits: ModelSerializer from Django REST framework
    """

    # Map 'sender_name' to the 'username' field of the UserProfile model
    sender_name = serializers.SlugRelatedField(many=False, slug_field='username', queryset=UserProfile.objects.all())

    # Map 'receiver_name' to the 'username' field of the UserProfile model
    receiver_name = serializers.SlugRelatedField(many=False, slug_field='username', queryset=UserProfile.objects.all())

    class Meta:
        # Specify the model to serialize
        model = Messages

        # Specify the fields to include in the serialized representation
        fields = ['sender_name', 'receiver_name', 'description', 'time']


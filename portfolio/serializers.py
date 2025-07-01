from rest_framework import serializers
from .models import Project, Skill, ContactMessage


class ProjectSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_image(self, obj):
        try:
            # Get the raw field value instead of .url to avoid MEDIA_URL prepending
            image_value = obj.image.name if obj.image else None
            if not image_value:
                return None

            # If it's already a full URL, return it as-is
            if image_value.startswith('http'):
                return image_value

            # Otherwise, build the full URL for relative paths
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{image_value}')
            return f'/media/{image_value}'
        except Exception:
            return None


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

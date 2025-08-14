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

            # Normalize paths to avoid doubling `/media/`
            # image_value may already include 'media/' or start with '/media/' or be just a filename
            if image_value.startswith('/media/'):
                path = image_value
            elif image_value.startswith('media/'):
                path = f'/{image_value.lstrip("/")}'
            else:
                path = f'/media/{image_value}'

            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
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

from rest_framework import serializers
from .models import Project, Skill, ContactMessage
from django.conf import settings
import os


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
            # Prefer serving the image from STATIC (collected assets) when available.
            # Use the filename only and check STATIC_ROOT for the file (collectstatic should have placed it there).
            filename = os.path.basename(image_value)

            # Check common locations inside STATIC_ROOT (direct or inside assets/)
            static_candidate_1 = os.path.join(settings.STATIC_ROOT or '', filename)
            static_candidate_2 = os.path.join(settings.STATIC_ROOT or '', 'assets', filename)

            request = self.context.get('request')

            if settings.STATIC_ROOT and (os.path.exists(static_candidate_1) or os.path.exists(static_candidate_2)):
                # Serve from STATIC_URL
                static_path = settings.STATIC_URL + filename
                if request:
                    return request.build_absolute_uri(static_path)
                return static_path

            # Normalize paths to avoid doubling `/media/`
            if image_value.startswith('/media/'):
                path = image_value
            elif image_value.startswith('media/'):
                path = f'/{image_value.lstrip("/")}'
            else:
                path = f'/media/{image_value}'

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

from rest_framework import serializers
from .models import Project, Skill, ContactMessage, BlogPost, Service, ServiceInquiry, Credential
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


class BlogPostSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'author',
            'featured_image', 'tags', 'published', 'created_at',
            'updated_at', 'published_date', 'read_time'
        ]
    
    def get_tags(self, obj):
        """Return tags as a list"""
        return obj.get_tags_list()
    
    def get_featured_image(self, obj):
        """Handle featured image URL similar to project images"""
        try:
            if not obj.featured_image:
                return None
            
            image_value = obj.featured_image.name
            if image_value.startswith('http'):
                return image_value
            
            filename = os.path.basename(image_value)
            static_candidate_1 = os.path.join(settings.STATIC_ROOT or '', filename)
            static_candidate_2 = os.path.join(settings.STATIC_ROOT or '', 'assets', filename)
            
            # Check if file exists in static locations
            if os.path.exists(static_candidate_1):
                path = f"{settings.STATIC_URL}{filename}"
            elif os.path.exists(static_candidate_2):
                path = f"{settings.STATIC_URL}assets/{filename}"
            else:
                # Fallback to media URL
                path = obj.featured_image.url
            
            # Make it absolute if we have a request context
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
        except Exception:
            return None


class ServiceSerializer(serializers.ModelSerializer):
    features_list = serializers.ReadOnlyField(source='get_features_list')
    
    class Meta:
        model = Service
        fields = '__all__'


class ServiceInquirySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = ServiceInquiry
        fields = '__all__'
        read_only_fields = ['created_at']


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'
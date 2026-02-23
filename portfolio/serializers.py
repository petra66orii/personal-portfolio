from rest_framework import serializers
from .models import Project, ContactMessage, BlogPost, Service, ServiceInquiry

class ProjectSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url


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
        return obj.get_tags_list()
    
    def get_featured_image(self, obj):
        if not obj.featured_image:
            return None
        return obj.featured_image.url


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
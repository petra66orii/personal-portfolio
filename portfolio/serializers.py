from rest_framework import serializers
from .models import Project, Skill, ContactMessage


class ProjectSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

        def get_image(self, obj):
            if obj.image:
                url = obj.image.url
                if url.startswith('http'):
                    return url
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(url)
                return url
            return None


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

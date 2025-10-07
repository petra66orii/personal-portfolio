from modeltranslation.translator import register, TranslationOptions
from .models import Project, Skill, Service, BlogPost

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('description', 'tech_stack')

@register(Skill)
class SkillTranslationOptions(TranslationOptions):
    fields = ('level', )

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'starting_price', 'delivery_time')

@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'tags', 'read_time')

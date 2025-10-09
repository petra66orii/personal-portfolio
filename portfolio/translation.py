from modeltranslation.translator import register, TranslationOptions
from .models import Project, Service, BlogPost

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('description', 'client_challenge', 'my_solution', 'the_result')

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'features', 'starting_price', 'delivery_time')


@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'tags', 'read_time')

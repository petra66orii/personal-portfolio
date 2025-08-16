from django.contrib import admin
from .models import Project, Skill, ContactMessage, BlogPost

# Register your models here.
admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(ContactMessage)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published', 'published_date', 'created_at']
    list_filter = ['published', 'published_date', 'created_at']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('author', 'tags', 'read_time')
        }),
        ('Publishing', {
            'fields': ('published', 'published_date')
        }),
    )

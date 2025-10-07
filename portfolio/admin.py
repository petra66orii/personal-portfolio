from django.contrib import admin
from .models import Project, ContactMessage, BlogPost, Service, ServiceInquiry, Credential

# Register your models here.
admin.site.register(Project)
admin.site.register(ContactMessage)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'featured', 'active', 'order']
    list_filter = ['service_type', 'featured', 'active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['featured', 'active', 'order']


@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service', 'budget_range', 'timeline', 'created_at', 'responded']
    list_filter = ['service', 'budget_range', 'timeline', 'responded', 'created_at']
    search_fields = ['name', 'email', 'company', 'project_details']
    readonly_fields = ['created_at']
    list_editable = ['responded']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


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

@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuing_organization', 'issue_date', 'expiration_date']
    search_fields = ['name', 'issuing_organization', 'credential_id']
    list_filter = ['issuing_organization', 'issue_date', 'expiration_date']
from django.contrib import admin
from .models import Project, ContactMessage, BlogPost, Service, ServiceInquiry
from django_summernote.admin import SummernoteModelAdmin

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


class BlogPostAdmin(SummernoteModelAdmin):
    # This tells Summernote which field needs the rich text editor
    summernote_fields = ('content',) 
    
    # Optional: Standard admin configurations
    list_display = ('title', 'created_at')
    search_fields = ['title', 'content']

admin.site.register(BlogPost, BlogPostAdmin)
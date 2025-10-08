from django.db import models
from django.utils.text import slugify

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to='',
        default='/default-project.png'
        )
    repo_link = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    tech_stack = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Service(models.Model):
    SERVICE_TYPES = [
        ('web_development', 'Web Development'),
        ('maintenance', 'Website Maintenance'),
        ('consultation', 'Technical Consultation'),
        ('optimization', 'Performance Optimization'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    short_description = models.CharField(max_length=200, help_text="Brief description for cards")
    description = models.TextField()
    features = models.TextField(help_text="One feature per line")
    starting_price = models.CharField(max_length=50, blank=True, help_text="e.g., 'From £500' or 'Contact for Quote'")
    delivery_time = models.CharField(max_length=50, blank=True, help_text="e.g., '2-3 weeks'")
    icon = models.CharField(max_length=50, default='code', help_text="Lucide icon name")
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_features_list(self):
        """Return features as a list"""
        return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
    
    def __str__(self):
        return self.name


class ServiceInquiry(models.Model):
    BUDGET_RANGES = [
        ('under_1k', 'Under €1,000'),
        ('1k_5k', '€1,000 - €5,000'),
        ('5k_10k', '€5,000 - €10,000'),
        ('10k_plus', '€10,000+'),
        ('not_sure', 'Not sure yet'),
    ]
    
    TIMELINE_CHOICES = [
        ('asap', 'ASAP'),
        ('1_month', 'Within 1 month'),
        ('2_3_months', '2-3 months'),
        ('flexible', 'Flexible'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=100, blank=True)
    project_details = models.TextField()
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGES, blank=True)
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website_url = models.URLField(blank=True, help_text="Current website if any")
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Service Inquiries"
    
    def __str__(self):
        service_name = self.service.name if self.service else "General Inquiry"
        return f"{self.name} - {service_name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=300, help_text="Brief description of the post")
    content = models.TextField()
    author = models.CharField(max_length=100, default="Miss Bott")
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    tags = models.CharField(max_length=255, help_text="Comma-separated tags")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    read_time = models.IntegerField(blank=True, null=True, help_text="Estimated read time in minutes")
    
    class Meta:
        ordering = ['-published_date', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def __str__(self):
        return self.title
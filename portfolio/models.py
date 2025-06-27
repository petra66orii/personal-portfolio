from django.db import models


# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to='media/',
        default='/default-project.png'
        )
    repo_link = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    tech_stack = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Skill(models.Model):
    name = models.CharField(max_length=50)
    # Level: Beginner, Intermediate, Expert
    level = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

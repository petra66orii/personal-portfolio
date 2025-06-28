from django.core.management.base import BaseCommand
from django.core import serializers
from portfolio.models import Project
import json
import os

class Command(BaseCommand):
    help = 'Export all projects to a JSON file for production deployment'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        
        if not projects.exists():
            self.stdout.write(self.style.WARNING('No projects found in database.'))
            return
        
        # Export to JSON
        projects_data = []
        for project in projects:
            project_dict = {
                'title': project.title,
                'description': project.description,
                'tech_stack': project.tech_stack,
                'repo_link': project.repo_link,
                'live_link': project.live_link,
                'featured': project.featured,
                'image': str(project.image) if project.image else 'default-project.png'
            }
            projects_data.append(project_dict)
        
        # Save to file
        export_file = 'portfolio/management/commands/projects_data.json'
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(projects_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {len(projects_data)} projects to {export_file}'
            )
        )
        
        # Also print the data for manual copying if needed
        self.stdout.write('\n--- Projects Data ---')
        for project in projects_data:
            self.stdout.write(f"Title: {project['title']}")
            self.stdout.write(f"Featured: {project['featured']}")
            self.stdout.write(f"Tech Stack: {project['tech_stack']}")
            self.stdout.write('---')

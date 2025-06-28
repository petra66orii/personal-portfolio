from django.core.management.base import BaseCommand
from django.core.management import call_command
from portfolio.models import Project
import json
import os


class Command(BaseCommand):
    help = 'Set up production database with migrations and your actual projects'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up production database...'))
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', '--verbosity=2')
        
        # Check if we already have projects
        if Project.objects.exists():
            self.stdout.write(self.style.WARNING(
                f'Database already has {Project.objects.count()} projects. Skipping data creation.'
            ))
            return
        
        # Try to load projects from JSON file first
        projects_data = self.load_projects_from_json()
        
        # If no JSON file, use default projects
        if not projects_data:
            projects_data = self.get_default_projects()
        
        # Create projects
        self.stdout.write(f'Creating {len(projects_data)} projects...')
        
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
            if created:
                self.stdout.write(f'Created project: {project.title}')
            else:
                self.stdout.write(f'Project already exists: {project.title}')
        
        self.stdout.write(self.style.SUCCESS('Production database setup completed successfully!'))

    def load_projects_from_json(self):
        """Load projects from exported JSON file"""
        json_file = os.path.join(os.path.dirname(__file__), 'projects_data.json')
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    projects_data = json.load(f)
                self.stdout.write(f'Loaded {len(projects_data)} projects from JSON file')
                return projects_data
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error loading JSON file: {e}'))
        return None

    def get_default_projects(self):
        """Return default projects if no JSON file exists"""
        self.stdout.write('Using default sample projects')
        return [
            {
                'title': 'Personal Portfolio Website',
                'description': 'A full-stack portfolio website built with React, Django, and PostgreSQL. Features dark mode, responsive design, and a nature-inspired theme.',
                'tech_stack': 'React, TypeScript, Tailwind CSS, Django, PostgreSQL',
                'repo_link': 'https://github.com/yourusername/personal-portfolio',
                'live_link': 'https://personal-portfolio-delta-olive.vercel.app',
                'featured': True,
                'image': 'default-project.png'
            },
            {
                'title': 'Task Management App',
                'description': 'A collaborative task management application with real-time updates and user authentication.',
                'tech_stack': 'React, Node.js, Express, MongoDB',
                'repo_link': 'https://github.com/yourusername/task-manager',
                'featured': True,
                'image': 'default-project.png'
            },
            {
                'title': 'Weather Dashboard',
                'description': 'A responsive weather dashboard that displays current conditions and forecasts using external APIs.',
                'tech_stack': 'JavaScript, HTML, CSS, OpenWeather API',
                'repo_link': 'https://github.com/yourusername/weather-dashboard',
                'featured': False,
                'image': 'default-project.png'
            }
        ]

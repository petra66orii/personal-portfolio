from django.core.management.base import BaseCommand
from django.core.management import call_command
from portfolio.models import Project

class Command(BaseCommand):
    help = 'Set up production database with migrations and sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up production database...'))
        
        # Run migrations
        self.stdout.write('Running migrations...')
        call_command('migrate', '--verbosity=2')
        
        # Check if we already have projects
        if Project.objects.exists():
            self.stdout.write(self.style.WARNING(
                f'Database already has {Project.objects.count()} projects. Skipping sample data creation.'
            ))
            return
        
        # Create sample projects for production
        self.stdout.write('Creating sample projects...')
        
        sample_projects = [
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
        
        for project_data in sample_projects:
            project, created = Project.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
            if created:
                self.stdout.write(f'Created project: {project.title}')
            else:
                self.stdout.write(f'Project already exists: {project.title}')
        
        self.stdout.write(self.style.SUCCESS('Production database setup completed successfully!'))

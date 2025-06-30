import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup media files for production deployment'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up media files...')
        
        # Ensure media directory exists
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir, exist_ok=True)
        
        # Copy default project image if it doesn't exist in media folder
        default_image_name = 'default-project.png'
        source_path = os.path.join(
            settings.BASE_DIR, 'media', default_image_name
        )
        dest_path = os.path.join(media_dir, default_image_name)
        
        if os.path.exists(source_path) and not os.path.exists(dest_path):
            try:
                shutil.copy2(source_path, dest_path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Copied {default_image_name} to media directory'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error copying {default_image_name}: {e}'
                    )
                )
        elif os.path.exists(dest_path):
            self.stdout.write(
                f'✓ {default_image_name} already exists in media directory'
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠ Source file {source_path} not found')
            )
        
        # List media directory contents
        self.stdout.write('Media directory contents:')
        try:
            for item in os.listdir(media_dir):
                self.stdout.write(f'  - {item}')
        except OSError as e:
            self.stdout.write(
                self.style.ERROR(f'Error listing media directory: {e}')
            )
        
        self.stdout.write(self.style.SUCCESS('Media setup complete!'))

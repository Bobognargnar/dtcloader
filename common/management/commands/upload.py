from django.core.management.base import BaseCommand
from common.models import File
import os

class Command(BaseCommand):
    """Upload command to load one or more file into the database.

    Usage: python manage.py upload file1 file2 <...>
    """

    help = 'Upload one or more Data Flow files to the database. Usage: python manage.py upload file1 file2 <...>'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='+', type=str, help='Files to upload')
        

    def handle(self, *args, **options):
        self.stdout.write(f"Uploading files from command line...")
        
        if not args:
            self.stdout.write(f"Please specify one or more files to upload")
            exit()
        
        for file in args:
            try:
                self.stdout.write(f"{file}...")
                filename = os.path.basename(file)

                # Prevent multiple submissions of the same file
                if not File.objects.filter(filename=filename).exists():
                    file_instance = File(filename = filename )
                    file_instance.file.save(os.path.basename(file), open(file, 'rb'))
                else:
                    self.stdout.write(f"Duplicated file, will be ignored.")
            except NotImplementedError as e:
                self.stdout.write(f"{str(e)}, will be uploaded but not processed")
            except FileNotFoundError as e:
                self.stdout.write(f"{str(e)}, skipping")
            except Exception as e:
                raise
            
        self.stdout.write(f"Upload completed.")
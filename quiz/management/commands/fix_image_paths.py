from django.core.management.base import BaseCommand
from quiz.models import Question
import re
import requests

class Command(BaseCommand):
    help = 'Fixes image paths by reverting the last digit to 1 if the current image does not exist.'

    def handle(self, *args, **options):
        questions = Question.objects.filter(image_path__isnull=False)
        fixed_count = 0

        for question in questions:
            if question.image_path:
                # Check if the image exists
                try:
                    response = requests.head(question.image_path)
                except Exception as e:
                    self.stdout.write(f"Error checking {question.image_path}: {e}")
                    continue
                if response.status_code == 404:
                    # Try changing the last digit to 1
                    match = re.match(r'(.*?_img)\d+(.png)$', question.image_path)
                    if match:
                        base_path, ext = match.groups()
                        new_path = f"{base_path}1{ext}"
                        try:
                            new_response = requests.head(new_path)
                        except Exception as e:
                            self.stdout.write(f"Error checking {new_path}: {e}")
                            continue
                        if new_response.status_code == 200:
                            question.image_path = new_path
                            question.save()
                            fixed_count += 1
                            self.stdout.write(f"Fixed image path for Question {question.question_number}: {new_path}")
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} image paths')) 
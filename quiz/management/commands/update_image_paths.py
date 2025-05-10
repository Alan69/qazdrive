from django.core.management.base import BaseCommand
from quiz.models import Question
import re

class Command(BaseCommand):
    help = 'Updates image paths by incrementing the last digit in the filename'

    def handle(self, *args, **options):
        questions = Question.objects.filter(image_path__isnull=False)
        updated_count = 0

        for question in questions:
            if question.image_path:
                # Extract the base path and the number
                match = re.match(r'(.*?)(\d+)\.png$', question.image_path)
                if match:
                    base_path, number = match.groups()
                    # Increment the number
                    new_number = str(int(number) + 1)
                    # Create new path
                    new_path = f"{base_path}{new_number}.png"
                    
                    # Update the question
                    question.image_path = new_path
                    question.save()
                    updated_count += 1
                    self.stdout.write(f"Updated image path for Question {question.question_number}: {new_path}")

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} image paths')) 
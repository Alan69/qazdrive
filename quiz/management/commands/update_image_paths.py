from django.core.management.base import BaseCommand
from quiz.models import Question
from django.conf import settings

class Command(BaseCommand):
    help = 'Update image paths to include full media URL'

    def handle(self, *args, **options):
        try:
            # Get all questions with image paths
            questions = Question.objects.exclude(image_path__isnull=True).exclude(image_path='')
            
            updated_count = 0
            for question in questions:
                if question.image_path:
                    # Remove any existing https://sapapdd.kz/media/ prefix if it exists
                    path = question.image_path
                    if path.startswith('https://sapapdd.kz/media/'):
                        path = path.replace('https://sapapdd.kz/media/', '')
                    if path.startswith('images/images/'):
                        path = path.replace('images/images/', 'images/')
                    
                    # Add the full URL
                    new_path = f'https://sapapdd.kz/media/{path}'
                    
                    # Update the question
                    question.image_path = new_path
                    question.save()
                    updated_count += 1
                    
                    self.stdout.write(f'Updated image path for question {question.question_number}: {new_path}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} image paths')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating image paths: {str(e)}')
            ) 
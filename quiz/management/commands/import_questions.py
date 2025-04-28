import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from quiz.models import Question, QuestionTranslation, QuestionOption

class Command(BaseCommand):
    help = 'Import questions from questions_corrected.json file'

    def handle(self, *args, **options):
        # Path to the JSON file
        json_file_path = os.path.join(settings.BASE_DIR, 'questions_corrected.json')
        
        # Check if file exists
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR('questions_corrected.json file not found'))
            return

        try:
            # Read and parse JSON file
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                questions = data.get('questions', [])

            # Clear existing data
            QuestionOption.objects.all().delete()
            QuestionTranslation.objects.all().delete()
            Question.objects.all().delete()

            # Import questions
            for question_data in questions:
                # Create Question
                question = Question.objects.create(
                    question_number=question_data['question_number'],
                    page=question_data['page'],
                    image_path=f"images/{question_data.get('image_path', '')}" if question_data.get('image_path') else None
                )

                # Create translations and options
                for translation_data in question_data['translations']:
                    # Find the index of the correct option
                    correct_option_index = None
                    options = translation_data['options']
                    
                    # Debug print
                    self.stdout.write(f"Processing question {question.question_number} in {translation_data['language']}")
                    self.stdout.write(f"Options: {[opt['is_correct'] for opt in options]}")
                    
                    # First try to find correct option from is_correct field
                    for i, option in enumerate(options):
                        if option.get('is_correct', False):
                            correct_option_index = i
                            break
                    
                    # If not found, try to get from correct_option_index
                    if correct_option_index is None:
                        correct_option_index = translation_data.get('correct_option_index')
                    
                    # If still not found, use first option as default
                    if correct_option_index is None:
                        correct_option_index = 0
                        self.stdout.write(self.style.WARNING(
                            f"No correct option found for question {question.question_number} in {translation_data['language']}, using first option"
                        ))

                    # Create translation
                    translation = QuestionTranslation.objects.create(
                        question=question,
                        language=translation_data['language'],
                        question_text=translation_data['question_text'],
                        correct_option_index=correct_option_index
                    )

                    # Create options
                    for option_data in options:
                        QuestionOption.objects.create(
                            translation=translation,
                            text=option_data['text'],
                            is_correct=option_data.get('is_correct', False)
                        )

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(questions)} questions'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing questions: {str(e)}'))
            # Print the problematic data
            if 'translation_data' in locals():
                self.stdout.write(self.style.ERROR(f'Problematic translation data: {translation_data}')) 
"""
Services for integrating students with existing quiz and course features
"""
from django.db.models import Count, Sum
from quiz.models import Result
from courses.models import UserVideoProgress


def get_student_quiz_results(student):
    """Get all quiz results for a student if they have a platform account"""
    if not student.user:
        return []
    
    return Result.objects.filter(user=student.user).order_by('-created')


def get_student_quiz_statistics(student):
    """Get quiz statistics for a student"""
    if not student.user:
        return {
            'total_attempts': 0,
            'passed': 0,
            'failed': 0,
            'average_score': 0
        }
    
    results = Result.objects.filter(user=student.user)
    total = results.count()
    
    if total == 0:
        return {
            'total_attempts': 0,
            'passed': 0,
            'failed': 0,
            'average_score': 0
        }
    
    # Assuming score format is "X/Y" or just a number
    passed = 0
    total_score = 0
    
    for result in results:
        try:
            score_str = result.score
            if '/' in score_str:
                correct, total_q = score_str.split('/')
                score_percent = (int(correct) / int(total_q)) * 100
            else:
                score_percent = float(score_str)
            
            total_score += score_percent
            if score_percent >= 90:  # 90% is passing in Kazakhstan
                passed += 1
        except (ValueError, ZeroDivisionError):
            continue
    
    return {
        'total_attempts': total,
        'passed': passed,
        'failed': total - passed,
        'average_score': round(total_score / total, 1) if total > 0 else 0
    }


def get_student_course_progress(student):
    """Get course video progress for a student"""
    if not student.user:
        return []
    
    progress = UserVideoProgress.objects.filter(
        user=student.user
    ).select_related('video', 'video__course').order_by('-watched_at')
    
    return progress


def get_student_course_statistics(student):
    """Get overall course completion statistics"""
    if not student.user:
        return {
            'total_videos': 0,
            'completed_videos': 0,
            'in_progress': 0,
            'completion_percentage': 0
        }
    
    progress = UserVideoProgress.objects.filter(user=student.user)
    completed = progress.filter(is_completed=True).count()
    total = progress.count()
    
    return {
        'total_videos': total,
        'completed_videos': completed,
        'in_progress': total - completed,
        'completion_percentage': round((completed / total) * 100) if total > 0 else 0
    }


def link_student_to_user(student, user):
    """Link a student record to a platform user account"""
    student.user = user
    student.save()
    
    # Also update registry verification since they have an account
    if not student.registry_verified:
        from django.utils import timezone
        student.registry_verified = True
        student.registry_verification_date = timezone.now()
        student.save()
    
    return student


def sync_student_category_from_group(student):
    """Sync student's category to their user account from their group"""
    if student.user and student.group and student.group.category:
        from quiz.models import Category
        
        # Try to find matching quiz category
        category = Category.objects.filter(
            cat_name__icontains=student.group.category.code
        ).first()
        
        if category:
            student.user.category = category
            student.user.save()
            return True
    
    return False


def get_student_readiness_for_exam(student):
    """
    Calculate if a student is ready for the driving exam
    Based on:
    - Theory quiz performance
    - Course completion
    - Practical hours completed
    """
    quiz_stats = get_student_quiz_statistics(student)
    course_stats = get_student_course_statistics(student)
    
    # Calculate practical hours from lessons
    from students.models import LessonRecord
    driving_hours = LessonRecord.objects.filter(
        student=student,
        lesson_type='driving',
        status='completed'
    ).aggregate(total=Sum('duration_minutes'))['total'] or 0
    
    driving_hours = driving_hours / 60  # Convert to hours
    
    # Requirements (typical for category B in Kazakhstan)
    REQUIRED_QUIZ_PASS_RATE = 90
    REQUIRED_COURSE_COMPLETION = 80
    REQUIRED_DRIVING_HOURS = 40
    
    readiness = {
        'quiz_ready': quiz_stats['average_score'] >= REQUIRED_QUIZ_PASS_RATE,
        'quiz_score': quiz_stats['average_score'],
        'course_ready': course_stats['completion_percentage'] >= REQUIRED_COURSE_COMPLETION,
        'course_completion': course_stats['completion_percentage'],
        'driving_ready': driving_hours >= REQUIRED_DRIVING_HOURS,
        'driving_hours': driving_hours,
        'driving_required': REQUIRED_DRIVING_HOURS,
        'overall_ready': False
    }
    
    readiness['overall_ready'] = all([
        readiness['quiz_ready'],
        readiness['course_ready'],
        readiness['driving_ready']
    ])
    
    return readiness


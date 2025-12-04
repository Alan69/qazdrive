from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def index(request):
    """
    Main landing page - redirects authenticated users to school dashboard,
    shows landing page for non-authenticated users
    """
    if request.user.is_authenticated:
        # Redirect to school dashboard (driving school mode)
        return redirect('schools:dashboard')
    
    # Show public landing page for non-authenticated users
    return render(request, 'main/landing.html')


@login_required(login_url='login')
def dashboard(request):
    """
    Legacy quiz dashboard - kept for backward compatibility
    Accessible via menu as secondary feature
    """
    from quiz.models import Result
    result = Result.objects.filter(user=request.user)
    context = {
        'result': result
    }
    return render(request, 'main/index.html', context=context)

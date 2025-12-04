"""qazdrive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from certificates.views import verify_certificate, verify_student
from userconf.admin_site import CustomAdminSite

# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

# Import all models to register them with our custom admin
from django.contrib import admin as django_admin
from django.apps import apps

# Auto-discover and register all admin modules
django_admin.autodiscover()

# Copy registrations from default admin to custom admin
for model, model_admin in django_admin.site._registry.items():
    admin_site.register(model, model_admin.__class__)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('main.urls')),
    path('login/', include('login.urls')),
    path('profile/', include('myprofile.urls')),
    path('payments/', include('payments.urls')),
    path('quiz/', include('quiz.urls')),
    path('subs_request/', include('subs_request.urls')),
    path('courses/', include('courses.urls')),
    
    # Avtomektep platform apps
    path('schools/', include('schools.urls')),
    path('staff/', include('staff.urls')),
    path('students/', include('students.urls')),
    path('tickets/', include('tickets.urls')),
    path('certificates/', include('certificates.urls')),
    
    # Public verification endpoints (no login required)
    path('verify/certificate/<uuid:uuid>/', verify_certificate, name='verify_certificate_public'),
    path('verify/student/', verify_student, name='verify_student_public'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
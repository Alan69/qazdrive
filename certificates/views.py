from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Certificate, CertificateVerification, CertificateTemplate
from .forms import CertificateForm
from schools.views import get_user_schools, get_current_school, school_required
from students.models import Student


@login_required
@school_required
def certificates_list(request):
    """List all certificates for the school"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    certificates = Certificate.objects.filter(school=school)
    
    if status_filter:
        certificates = certificates.filter(status=status_filter)
    
    if search:
        certificates = certificates.filter(
            certificate_number__icontains=search
        ) | certificates.filter(
            student__last_name__icontains=search
        ) | certificates.filter(
            student__first_name__icontains=search
        ) | certificates.filter(
            student__iin__icontains=search
        )
    
    certificates = certificates.select_related('student', 'category').order_by('-issue_date')
    
    paginator = Paginator(certificates, 20)
    page = request.GET.get('page', 1)
    certificates = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'certificates': certificates,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'certificates/certificates_list.html', context)


@login_required
@school_required
def certificate_create(request, student_id=None):
    """Create new certificate"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    initial = {}
    if student_id:
        student = get_object_or_404(Student, id=student_id, group__school=school)
        initial['student'] = student
        initial['category'] = student.group.category
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, school=school)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.school = school
            certificate.issued_by = request.user
            certificate.save()
            messages.success(request, 'Свидетельство создано')
            return redirect('certificates:detail', certificate_id=certificate.id)
    else:
        form = CertificateForm(school=school, initial=initial)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
    }
    return render(request, 'certificates/certificate_form.html', context)


@login_required
@school_required
def certificate_detail(request, certificate_id):
    """View certificate details"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    certificate = get_object_or_404(Certificate, id=certificate_id, school=school)
    
    verifications = certificate.verifications.all().order_by('-verified_at')[:10]
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'certificate': certificate,
        'verifications': verifications,
    }
    return render(request, 'certificates/certificate_detail.html', context)


@login_required
@school_required
def certificate_issue(request, certificate_id):
    """Issue (activate) a certificate"""
    school = request.current_school
    certificate = get_object_or_404(Certificate, id=certificate_id, school=school)
    
    if certificate.status != 'draft':
        messages.error(request, 'Только черновики могут быть выданы')
        return redirect('certificates:detail', certificate_id=certificate.id)
    
    certificate.status = 'issued'
    certificate.save()  # This will trigger QR code generation
    
    messages.success(request, 'Свидетельство выдано')
    return redirect('certificates:detail', certificate_id=certificate.id)


@login_required
@school_required
def certificate_revoke(request, certificate_id):
    """Revoke a certificate"""
    school = request.current_school
    certificate = get_object_or_404(Certificate, id=certificate_id, school=school)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        certificate.status = 'revoked'
        certificate.revocation_reason = reason
        certificate.revoked_at = timezone.now()
        certificate.revoked_by = request.user
        certificate.save()
        
        messages.success(request, 'Свидетельство отозвано')
        return redirect('certificates:detail', certificate_id=certificate.id)
    
    return redirect('certificates:detail', certificate_id=certificate.id)


@login_required
@school_required
def certificate_download(request, certificate_id):
    """Download certificate PDF"""
    school = request.current_school
    certificate = get_object_or_404(Certificate, id=certificate_id, school=school)
    
    if not certificate.pdf_file:
        messages.error(request, 'PDF файл не найден')
        return redirect('certificates:detail', certificate_id=certificate.id)
    
    response = HttpResponse(certificate.pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{certificate.certificate_number}.pdf"'
    return response


# Public verification views (no login required)
def verify_certificate(request, uuid):
    """Public certificate verification page"""
    from django.db.models import Q
    
    certificate = get_object_or_404(Certificate, uuid=uuid)
    
    # Log verification
    CertificateVerification.objects.create(
        certificate=certificate,
        verified_by=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        is_valid=certificate.is_valid,
        verification_message='Проверка через QR код' if certificate.is_valid else 'Свидетельство недействительно'
    )
    
    context = {
        'certificate': certificate,
        'is_valid': certificate.is_valid,
    }
    return render(request, 'certificates/verify.html', context)


def verify_certificate_api(request, uuid):
    """API endpoint for certificate verification"""
    try:
        certificate = Certificate.objects.get(uuid=uuid)
        
        # Log verification
        CertificateVerification.objects.create(
            certificate=certificate,
            verified_by=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_valid=certificate.is_valid,
            verification_message='API проверка'
        )
        
        return JsonResponse({
            'valid': certificate.is_valid,
            'certificate_number': certificate.certificate_number,
            'student_name': certificate.student.full_name,
            'school_name': certificate.school.name,
            'category': certificate.category.code if certificate.category else None,
            'issue_date': certificate.issue_date.isoformat() if certificate.issue_date else None,
            'status': certificate.status,
        })
    except Certificate.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'error': 'Свидетельство не найдено'
        }, status=404)


# Student registry verification
def verify_student(request):
    """Public student registry verification page"""
    iin = request.GET.get('iin', '')
    result = None
    
    if iin:
        student = Student.objects.filter(iin=iin, registry_verified=True).first()
        if student:
            result = {
                'found': True,
                'full_name': student.full_name,
                'school_name': student.school.name,
                'group_name': student.group.name,
                'category': student.group.category.code if student.group.category else 'N/A',
                'enrollment_date': student.enrollment_date,
                'status': student.get_status_display(),
            }
        else:
            result = {'found': False}
    
    context = {
        'iin': iin,
        'result': result,
    }
    return render(request, 'certificates/verify_student.html', context)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

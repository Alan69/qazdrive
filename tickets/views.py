from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from .models import Ticket, TicketMessage, TicketSubject, TicketNotification
from .forms import TicketForm, TicketMessageForm
from schools.views import get_user_schools, get_current_school, school_required


@login_required
def user_tickets_list(request):
    """List user's personal tickets (ДАННЫЕ ПОЛЬЗОВАТЕЛЯ section)"""
    user_schools = get_user_schools(request.user)
    
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page', 1)
    tickets = paginator.get_page(page)
    
    context = {
        'user_schools': user_schools,
        'tickets': tickets,
        'is_user_section': True,
    }
    return render(request, 'tickets/tickets_list.html', context)


@login_required
@school_required
def school_tickets_list(request):
    """List school's tickets (ДАННЫЕ АВТОШКОЛЫ section)"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    tickets = Ticket.objects.filter(school=school).order_by('-created_at')
    
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page', 1)
    tickets = paginator.get_page(page)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'tickets': tickets,
        'is_user_section': False,
    }
    return render(request, 'tickets/tickets_list.html', context)


@login_required
def ticket_create(request):
    """Create new ticket"""
    user_schools = get_user_schools(request.user)
    current_school = get_current_school(request)
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            # Optionally associate with current school
            if request.POST.get('associate_school') and current_school:
                ticket.school = current_school
            ticket.save()
            messages.success(request, 'Обращение создано')
            return redirect('tickets:detail', ticket_id=ticket.id)
    else:
        form = TicketForm()
    
    context = {
        'user_schools': user_schools,
        'form': form,
        'subjects': TicketSubject.objects.filter(is_active=True),
        'current_school': current_school,
    }
    return render(request, 'tickets/ticket_form.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """View ticket detail and conversation"""
    user_schools = get_user_schools(request.user)
    
    # User can only view their own tickets (unless admin)
    if request.user.is_superuser or request.user.is_platform_admin:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    # Mark messages as read
    ticket.messages.filter(is_admin_response=True, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    
    # Handle new message
    if request.method == 'POST':
        message_form = TicketMessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            
            # Reopen ticket if it was closed
            if ticket.status == 'closed':
                ticket.status = 'waiting'
                ticket.save()
            
            messages.success(request, 'Сообщение отправлено')
            return redirect('tickets:detail', ticket_id=ticket.id)
    else:
        message_form = TicketMessageForm()
    
    context = {
        'user_schools': user_schools,
        'ticket': ticket,
        'messages_list': ticket.messages.all().order_by('created_at'),
        'message_form': message_form,
    }
    return render(request, 'tickets/ticket_detail.html', context)


# Admin views for handling tickets
@login_required
def admin_tickets_list(request):
    """Admin view for all tickets"""
    if not (request.user.is_superuser or request.user.is_platform_admin):
        messages.error(request, 'Доступ запрещен')
        return redirect('schools:dashboard')
    
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    tickets = Ticket.objects.all()
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    if search:
        tickets = tickets.filter(
            Q(user__phone_number__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(description__icontains=search)
        )
    
    tickets = tickets.order_by('-created_at')
    
    paginator = Paginator(tickets, 20)
    page = request.GET.get('page', 1)
    tickets = paginator.get_page(page)
    
    context = {
        'user_schools': user_schools,
        'tickets': tickets,
        'status_filter': status_filter,
        'search': search,
        'is_admin': True,
    }
    return render(request, 'tickets/admin_tickets_list.html', context)


@login_required
def admin_ticket_detail(request, ticket_id):
    """Admin view for ticket detail with ability to respond"""
    if not (request.user.is_superuser or request.user.is_platform_admin):
        messages.error(request, 'Доступ запрещен')
        return redirect('schools:dashboard')
    
    user_schools = get_user_schools(request.user)
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Handle admin response
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'respond':
            message_form = TicketMessageForm(request.POST, request.FILES)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.ticket = ticket
                message.sender = request.user
                message.is_admin_response = True
                message.save()
                
                # Update ticket status
                ticket.status = 'in_progress'
                if not ticket.assigned_admin:
                    ticket.assigned_admin = request.user
                ticket.save()
                
                messages.success(request, 'Ответ отправлен')
                return redirect('tickets:admin_detail', ticket_id=ticket.id)
        
        elif action == 'close':
            ticket.status = 'closed'
            ticket.resolved_at = timezone.now()
            ticket.resolution = request.POST.get('resolution', '')
            ticket.save()
            messages.success(request, 'Заявка закрыта')
            return redirect('tickets:admin_detail', ticket_id=ticket.id)
        
        elif action == 'assign':
            ticket.assigned_admin = request.user
            ticket.status = 'in_progress'
            ticket.save()
            messages.success(request, 'Заявка назначена вам')
            return redirect('tickets:admin_detail', ticket_id=ticket.id)
    
    message_form = TicketMessageForm()
    
    context = {
        'user_schools': user_schools,
        'ticket': ticket,
        'messages_list': ticket.messages.all().order_by('created_at'),
        'message_form': message_form,
        'is_admin': True,
    }
    return render(request, 'tickets/admin_ticket_detail.html', context)

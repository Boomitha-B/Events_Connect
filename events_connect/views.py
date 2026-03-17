from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Event, RSVP
from .forms import EventForm
from .auth_forms import SignUpForm

# Role-Based Access Control Helper
def is_admin(user):
    return user.is_staff

def home(request):
    query = request.GET.get('q', '')
    dept_filter = request.GET.get('dept', '')
    
    # RBAC: Admins see all events, Students see only active events
    if request.user.is_staff:
        events = Event.objects.all().order_by('-date', '-time')
    else:
        events = Event.objects.filter(is_active=True).order_by('-date', '-time')
    
    if query:
        events = events.filter(title__icontains=query) | events.filter(description__icontains=query)
    
    if dept_filter:
        events = events.filter(department__iexact=dept_filter)
        
    departments = Event.objects.values_list('department', flat=True).distinct()
        
    return render(request, 'home.html', {
        'events': events,
        'departments': departments,
        'current_query': query,
        'current_dept': dept_filter
    })

def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    is_attending = False
    
    if request.user.is_authenticated:
        is_attending = RSVP.objects.filter(user=request.user, event=event).exists()
        
    attendee_count = event.rsvps.count()
    
    return render(request, 'event_detail.html', {
        'event': event,
        'is_attending': is_attending,
        'attendee_count': attendee_count
    })

@user_passes_test(is_admin, login_url='login')
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            messages.success(request, 'Event successfully created!')
            return redirect('home')
    else:
        form = EventForm()
        
    return render(request, 'create_event.html', {'form': form})
    
@user_passes_test(is_admin, login_url='login')
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
        
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event successfully updated!')
            return redirect('event_detail', id=event.id)
    else:
        form = EventForm(instance=event)
        
    return render(request, 'create_event.html', {'form': form, 'is_edit': True, 'event': event})

@user_passes_test(is_admin, login_url='login')
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.success(request, "Event has been deleted.")
        
    return redirect('home')

@user_passes_test(is_admin, login_url='login')
def toggle_event_status(request, id):
    event = get_object_or_404(Event, id=id)
    event.is_active = not event.is_active
    event.save()
    status_str = "activated" if event.is_active else "deactivated"
    messages.success(request, f'Event "{event.title}" has been {status_str}.')
    return redirect('event_detail', id=event.id)

@login_required(login_url='login')
def rsvp_event(request, id):
    event = get_object_or_404(Event, id=id)
    
    # Toggle RSVP status
    rsvp_qs = RSVP.objects.filter(user=request.user, event=event)
    if rsvp_qs.exists():
        rsvp_qs.delete()
        messages.info(request, f"You are no longer attending '{event.title}'.")
    else:
        RSVP.objects.create(user=request.user, event=event)
        messages.success(request, f"You have successfully joined '{event.title}'!")
        
    return redirect('event_detail', id=event.id)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome to EventsHub!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('home')
        else:
            messages.error(request, 'You are already logged in as a student.')
            return redirect('home')
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f'Admin Session Started: Welcome back, {username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Access Denied: You do not have administration privileges.')
            else:
                messages.error(request, 'Invalid admin username or password.')
        else:
            messages.error(request, 'Invalid admin username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

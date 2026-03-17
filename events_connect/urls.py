from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('event/<int:id>/', views.event_detail, name='event_detail'),
    path('event/<int:id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:id>/toggle-status/', views.toggle_event_status, name='toggle_event_status'),
    path('event/<int:id>/rsvp/', views.rsvp_event, name='rsvp_event'),

    path('event/new/', views.create_event, name='create_event'),
]

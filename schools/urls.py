from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    # School list and management
    path('', views.school_list, name='school_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('switch/<int:school_id>/', views.switch_school, name='switch_school'),
    
    # School profile
    path('profile/', views.school_profile, name='profile'),
    path('profile/edit/', views.school_edit, name='edit'),
    
    # Cabinets
    path('cabinets/', views.cabinets_list, name='cabinets'),
    path('cabinets/add/', views.cabinet_add, name='cabinet_add'),
    path('cabinets/<int:cabinet_id>/edit/', views.cabinet_edit, name='cabinet_edit'),
    
    # Vehicles
    path('transport/', views.vehicles_list, name='vehicles'),
    path('transport/add/', views.vehicle_add, name='vehicle_add'),
    path('transport/<int:vehicle_id>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('transport/<int:vehicle_id>/delete/', views.vehicle_delete, name='vehicle_delete'),
    
    # Catalog cards
    path('school-cards/', views.catalog_cards_list, name='catalog_cards'),
    path('school-cards/add/', views.catalog_card_add, name='catalog_card_add'),
    path('school-cards/<int:card_id>/edit/', views.catalog_card_edit, name='catalog_card_edit'),
    path('school-cards/<int:card_id>/toggle/', views.catalog_card_toggle, name='catalog_card_toggle'),
    
    # Transactions
    path('transactions/', views.transactions_list, name='transactions'),
    
    # Contracts
    path('contracts/', views.contracts_list, name='contracts'),
]


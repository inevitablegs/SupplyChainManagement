from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.supplier_register, name='supplier_register'),
    path('login/', views.supplier_login, name='supplier_login'),
    path('dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('bid/<int:quote_id>/', views.submit_bid, name='submit_bid'),
    path('profile/', views.view_profile, name='supplier_profile'),
    path('profile/edit/', views.edit_profile, name='supplier_edit_profile'),
    path('manufacturer-profile/<int:manufacturer_id>/', views.view_manufacturer_profile, name='view_manufacturer_profile'),
]
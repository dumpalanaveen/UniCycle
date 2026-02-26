from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cycle/<int:pk>/', views.cycle_detail_view, name='cycle_detail'),
    path('cycle/<int:pk>/book/', views.book_cycle_view, name='book_cycle'),
    path('booking/<int:booking_id>/payment/', views.payment_view, name='payment'),
    path('booking/<int:booking_id>/success/', views.booking_success_view, name='booking_success'),
    path('booking/<int:booking_id>/return/', views.return_cycle_view, name='return_cycle'),
    path('booking/<int:booking_id>/return-summary/', views.return_summary_view, name='return_summary'),
    path('profile/', views.profile_view, name='profile'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
]

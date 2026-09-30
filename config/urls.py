from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from crm_core.views import (
    place_status_list, start_session_api, stop_session, 
    get_recommendation, manager_stats, prolong_session, clients_list, tariffs_list,
    manage_tariffs, tariff_detail, manage_promotions, promotion_detail,
    create_booking_api, my_bookings_api, cancel_booking_api,
    analytics_revenue, analytics_occupancy, analytics_clients,
    analytics_sessions, analytics_bookings,
    confirm_booking_api, all_bookings_list
)
from loyalty.views import client_info_api, register_client_api, apply_referral_api, referral_stats_api

def landing_page(request):
    return render(request, 'landing.html')

def operations_dashboard(request):
    return render(request, 'operations_dashboard.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page),  # Root URL
    # All dashboards now point to operations_dashboard
    path('dashboard/', operations_dashboard),
    path('dispatcher/', operations_dashboard), 
    path('manager/', operations_dashboard),
    path('operations/', operations_dashboard),
    
    # API Endpoints
    path('api/place_status/', place_status_list),
    path('api/start_session/', start_session_api),
    path('api/stop_session/<int:session_id>/', stop_session),
    path('api/prolong_session/', prolong_session),
    path('api/client_info/<int:telegram_id>/', client_info_api),
    path('api/register_client/', register_client_api),
    path('api/recommendations/<int:place_id>/', get_recommendation),
    path('api/manager_stats/', manager_stats),
    path('api/clients/', clients_list),
    path('api/tariffs/', tariffs_list),
    
    # Referral & Booking APIs
    path('api/apply_referral/', apply_referral_api),
    path('api/referral_stats/<int:telegram_id>/', referral_stats_api),
    path('api/create_booking/', create_booking_api),
    path('api/my_bookings/<int:telegram_id>/', my_bookings_api),
    path('api/cancel_booking/<int:booking_id>/', cancel_booking_api),
    path('api/confirm_booking/<int:booking_id>/', confirm_booking_api),
    path('api/all_bookings/', all_bookings_list),
    
    # Management APIs
    path('api/tariffs/manage/', manage_tariffs),
    path('api/tariffs/<int:pk>/', tariff_detail),
    path('api/promotions/', manage_promotions),
    path('api/promotions/<int:pk>/', promotion_detail),
    
    # Extended Analytics APIs
    path('api/analytics/revenue/', analytics_revenue),
    path('api/analytics/occupancy/', analytics_occupancy),
    path('api/analytics/clients/', analytics_clients),
    path('api/analytics/sessions/', analytics_sessions),
    path('api/analytics/bookings/', analytics_bookings),
]

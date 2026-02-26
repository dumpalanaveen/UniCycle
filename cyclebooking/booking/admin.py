from django.contrib import admin
from .models import Cycle, Booking, UserProfile


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('name', 'cycle_id', 'color', 'gear_type', 'condition', 'status', 'added_on')
    list_filter = ('status', 'gear_type', 'condition')
    search_fields = ('name', 'cycle_id', 'color')
    list_editable = ('status',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'cycle', 'duration_minutes', 'total_cost',
        'actual_duration_minutes', 'refund_amount', 'status',
        'unlock_pin', 'booking_date', 'returned_at'
    )
    list_filter = ('status',)
    search_fields = ('user__username', 'cycle__name', 'unlock_pin', 'payment_reference')
    readonly_fields = ('unlock_pin', 'payment_reference', 'qr_data', 'total_cost')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'department', 'phone')
    search_fields = ('user__username', 'roll_number', 'department')

from django.contrib import admin
from .models import Department, Employee, Equipment, MovementHistory


class MovementHistoryInline(admin.TabularInline):
    model = MovementHistory
    extra = 0
    readonly_fields = ('from_department', 'to_department', 'responsible', 'date')
    can_delete = False


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'status', 'department')
    list_filter = ('department', 'status')
    search_fields = ('name', 'serial_number')
    readonly_fields = ('qr_code',)
    fields = ('name', 'serial_number', 'status', 'department', 'qr_code')
    inlines = [MovementHistoryInline]


admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(MovementHistory)